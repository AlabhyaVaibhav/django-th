# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied

from django.views.generic import CreateView, UpdateView, \
    DeleteView, ListView, TemplateView, FormView

from django.contrib.formtools.wizard.views import SessionWizardView

# trigger_happy
from django_th.models import TriggerService, UserService, ServicesActivated
from django_th.forms.base import TriggerServiceRssEvernoteForm, UserServiceForm

from th_rss.models import Rss
from th_evernote.models import Evernote

from django_th.services import default_provider


import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.contrib.auth import logout

default_provider.load_services()

#************************
# FBV : simple actions  *
#************************

def qty_services_activated(user):
    """
        get the quantity of activated services
    """
    return UserService.objects.filter(user=user)

def logout_view(request):
    """
        logout the user then redirect him to the home page
    """
    logout(request)
    return redirect('base')


def trigger_on_off(request, trigger_id):
    """
        switch the status of the trigger then go back home
    """
    trigger = TriggerService.objects.get(id=trigger_id)
    if trigger.status:
        trigger.status = False
    else:
        trigger.status = True
    trigger.save()

    return redirect('base')


def edit_trigger_rss_evernote(request, trigger_id):
    """
        load the form from the Trigger ID and data from 3 models
    """
    if request.user.is_authenticated():
        service = TriggerService.objects.get(pk=trigger_id)
        if request.user == service.user:
            if request.method == 'POST':
                form = TriggerServiceRssEvernoteForm(request.POST)
                if form.is_valid():  # All validation rules pass
                    rss = Rss.objects.get(trigger=trigger_id)
                    evernote = Evernote.objects.get(trigger=trigger_id)

                    # service
                    service.description = form.cleaned_data['description']
                    if form.cleaned_data['status']:
                        service.status = 1
                    else:
                        service.status = 0

                    service.save()
                    # rss
                    rss.url = form.cleaned_data['url']
                    rss.save()

                    # evernote
                    evernote.tag = form.cleaned_data['tag']
                    evernote.notebook = form.cleaned_data['notebook']
                    evernote.save()

                    return HttpResponseRedirect('/trigger/edit/thanks/')  # Redirect after POST

            else:
                rss = Rss.objects.get(trigger=trigger_id)
                evernote = Evernote.objects.get(trigger=trigger_id)
                instance = {'trigger_id': service.id,
                            'description': service.description,
                            'status': service.status,

                            'url': rss.url,

                            'tag': evernote.tag,
                            'notebook': evernote.notebook}

                form = TriggerServiceRssEvernoteForm(
                    instance)  # An unbound form

            return render(request, 'triggers/edit_trigger_rss_evernote.html', {
                'form': form,
            })
        else:
            raise PermissionDenied
    else:
        raise PermissionDenied


#*************************************
#  Part I : the Triggers
#*************************************

class TriggerListView(ListView):
    context_object_name = "triggers_list"
    queryset = TriggerService.objects.all()
    template_name = "home.html"
    paginate_by = 7

    def get_queryset(self):
        # get the Trigger of the connected user
        if self.request.user.is_authenticated():
            return self.queryset.filter(user=self.request.user).\
                order_by('-date_created')
        # otherwise return nothing
        return TriggerService.objects.none()

    def get_context_data(self, **kw):
        enabled = disabled = ()
        if self.request.user.is_authenticated():
            #get the enabled triggers
            triggers_enabled = TriggerService.objects.filter(user=self.request.user, status=1)
            #get the disabled triggers
            triggers_disabled = TriggerService.objects.filter(user=self.request.user, status=0)
            #get the activated services
            services_activated = qty_services_activated(self.request.user)
        context = super(TriggerListView, self).get_context_data(**kw)
        context['nb_triggers'] = {'enabled': len(triggers_enabled), 'disabled': len(triggers_disabled)}
        context['nb_services'] = len(services_activated)
        return context


class TriggerEditedTemplateView(TemplateView):
    template_name = "triggers/thanks_trigger.html"

    def get_context_data(self, **kw):
        context = super(TriggerEditedTemplateView, self).get_context_data(**kw)
        context['sentance'] = 'Your trigger has been successfully modified'
        return context


class TriggerDeleteView(DeleteView):
    queryset = TriggerService.objects.all()
    template_name = "triggers/delete_trigger.html"
    success_url = '/trigger/delete/thanks/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TriggerDeleteView, self).dispatch(*args, **kwargs)


class TriggerDeletedTemplateView(TemplateView):
    template_name = "triggers/thanks_trigger.html"

    def get_context_data(self, **kw):
        context = super(TriggerDeletedTemplateView, self).\
            get_context_data(**kw)
        context['sentance'] = 'Your trigger has been successfully deleted'
        return context


#*************************************
#  Part II : the UserServices
#*************************************
class UserServiceListView(ListView):
    context_object_name = "services_list"
    queryset = UserService.objects.all()
    template_name = "services/services.html"

    def get_queryset(self):
        # get the Service of the connected user
        if self.request.user.is_authenticated():
            return self.queryset.filter(user=self.request.user)
        # otherwise return nothing
        return UserService.objects.none()

    def get_context_data(self, **kw):
        context = super(UserServiceListView, self).get_context_data(**kw)
        if self.request.user.is_authenticated():
            nb_user_service = UserService.objects.filter(user=self.request.user).count()
            nb_service = ServicesActivated.objects.all().count()
            if nb_user_service == nb_service:
                context['action'] = 'hide'
            else:
                context['action'] = 'display'
        return context


class UserServiceCreateView(CreateView):
    form_class = UserServiceForm
    template_name = "services/add_service.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserServiceCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(user=self.request.user)

        sa = ServicesActivated.objects.get(name=form.cleaned_data['name'])
        # let's build the 'call' of the auth method
        # which owns to a ServiceXXX class
        if sa.auth_required:
            # use the default_provider to get the object from the ServiceXXX
            service_object = default_provider.get_service(
                str(form.cleaned_data['name']))
            # get the class object
            lets_auth = getattr(service_object, 'auth')
            # call the auth func from this class
            # and redirect to the external service page
            # to auth the application django-th to access to the user
            # account details
            return redirect(lets_auth(self.request))

        return HttpResponseRedirect('/service/add/thanks/')

    def get_context_data(self, **kw):
        context = super(UserServiceCreateView, self).get_context_data(**kw)
        context['action'] = 'add_service'
        return context

    def get_form_kwargs(self, **kwargs):
        kwargs = super(UserServiceCreateView, self).get_form_kwargs(**kwargs)
        kwargs['initial']['user'] = self.request.user
        return kwargs

class UserServiceDeleteView(DeleteView):
    queryset = UserService.objects.all()
    template_name = "services/delete_service.html"
    success_url = '/service/delete/thanks/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserServiceDeleteView, self).dispatch(*args, **kwargs)


class UserServiceAddedTemplateView(TemplateView):
    template_name = "services/thanks_service.html"

    def get_context_data(self, **kw):
        context = super(UserServiceAddedTemplateView, self).\
            get_context_data(**kw)
        context['sentance'] = 'Your service has been successfully created'
        return context


class UserServiceDeletedTemplateView(TemplateView):
    template_name = "services/thanks_service.html"

    def get_context_data(self, **kw):
        context = super(UserServiceDeletedTemplateView, self).\
            get_context_data(**kw)
        context['sentance'] = 'Your service has been successfully deleted'
        return context


class UserServiceIndexView(ListView):

    """
        list of all available services activated from the admin
        the user can use and activate too for his own usage
    """
    context_object_name = "services_list"
    queryset = ServicesActivated.objects.all()
    template_name = "services/index.html"

    def get_queryset(self):
        return ServicesActivated.objects.none()


#*************************************
#  Part III : Service Wizard
#*************************************


from th_rss.forms import RssForm
from th_evernote.forms import EvernoteForm
from django_th.forms.base import ServicesDescriptionForm

FORMS = [("rss", RssForm),
         ("evernote", EvernoteForm),
         ("services", ServicesDescriptionForm), ]

TEMPLATES = {
    '0': 'rss/wz-rss-form.html',
    '1': 'evernote/wz-evernote-form.html',
    '2': 'services_wizard/wz-description.html'}


class UserServiceWizard(SessionWizardView):
    instance = None

    def get_form_instance(self, step):
        """
        Provides us with an instance of the Project Model to save on completion
        """

        if self.instance is None:
            self.instance = TriggerService()
        return self.instance

    def done(self, form_list, **kwargs):
        """
        Save info to the DB
        """

        trigger = self.instance
        trigger.provider = UserService.objects.get(
            name='ServiceRss',
            user=self.request.user)
        trigger.consummer = UserService.objects.get(name='ServiceEvernote',
                                                    user=self.request.user)
        trigger.user = self.request.user
        trigger.status = True
        # save the trigger
        trigger.save()
        #...then create the related services from the wizard
        for form in form_list:
            if form.cleaned_data['my_form_is'] == 'rss':
                from th_rss.models import Rss
                Rss.objects.create(
                    name=form.cleaned_data['name'],
                    url=form.cleaned_data['url'],
                    status=1,
                    trigger=trigger)
            if form.cleaned_data['my_form_is'] == 'evernote':
                from th_evernote.models import Evernote
                Evernote.objects.create(
                    tag=form.cleaned_data['tag'],
                    notebook=form.cleaned_data['notebook'],
                    status=1,
                    trigger=trigger)

        return HttpResponseRedirect('/')

    def get_template_names(self):
        """
            Custom templates for the different steps
        """
        return [TEMPLATES[self.steps.current]]


def finalcallback(request, **kwargs):
    """
        let's do the callback of the related service after
        the auth request from UserServiceCreateView
    """
    service_name = kwargs['service_name']
    service_object = default_provider.get_service(service_name)
    lets_callback = getattr(service_object, 'callback')
    # call the auth func from this class
    # and redirect to the external service page
    # to auth the application django-th to access to the user
    # account details
    return render_to_response(lets_callback(request))
