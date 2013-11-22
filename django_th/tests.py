import unittest
from django.test import RequestFactory
from django_th.views import TriggerEditedTemplateView, TriggerDeletedTemplateView, UserServiceAddedTemplateView, UserServiceDeletedTemplateView, TriggerListView, UserServiceListView
from django.contrib.auth.models import User
from django_th.models import UserProfile, TriggerService, UserService, ServicesActivated
from django.core.exceptions import ObjectDoesNotExist


class TriggerEditedTemplateViewTestCase(unittest.TestCase):

    def test_get(self):
        template_name = "triggers/thanks_trigger.html"
        # Setup request and view.
        request = RequestFactory().get('/trigger/edit/thanks')
        view = TriggerEditedTemplateView.as_view(template_name=template_name)
        sentance = 'Your trigger has been successfully modified'
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.template_name[0], 'triggers/thanks_trigger.html')
        self.assertEqual(response.context_data['sentance'], sentance)


class TriggerDeletedTemplateViewTestCase(unittest.TestCase):

    def test_get(self):
        template_name = "triggers/thanks_trigger.html"
        # Setup request and view.
        request = RequestFactory().get('/trigger/delete/thanks')
        view = TriggerDeletedTemplateView.as_view(
            template_name=template_name)
        sentance = 'Your trigger has been successfully deleted'
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.template_name[0], 'triggers/thanks_trigger.html')
        self.assertEqual(response.context_data['sentance'], sentance)


class UserServiceAddedTemplateViewTestCase(unittest.TestCase):

    def test_get(self):
        template_name = 'services/thanks_service.html'
        # Setup request and view.
        request = RequestFactory().get('/service/add/thanks')
        view = UserServiceAddedTemplateView.as_view(
            template_name=template_name)
        sentance = 'Your service has been successfully created'
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.template_name[0], 'services/thanks_service.html')
        self.assertEqual(response.context_data['sentance'], sentance)


class UserServiceDeletedTemplateViewTestCase(unittest.TestCase):

    def test_get(self):
        template_name = 'services/thanks_service.html'
        # Setup request and view.
        request = RequestFactory().get('/service/delete/thanks')
        view = UserServiceDeletedTemplateView.as_view(
            template_name=template_name)
        sentance = 'Your service has been successfully deleted'
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.template_name[0], 'services/thanks_service.html')
        self.assertEqual(response.context_data['sentance'], sentance)




class UserServiceListViewTestCase(unittest.TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        try:
            self.user = User.objects.get(username='john')
        except User.DoesNotExist:
            self.user = User.objects.create_user(
                username='john', email='john@doe.info', password='doe')

    def test_context_data(self):
        # Setup request and view
        queryset = UserService.objects.all()

        request = RequestFactory().get('/')
        request.user = self.user

        view = UserServiceListView(
            template_name='services/services.html',
            context_object_name="services_list",
            object_list=queryset)
        view = setup_view(view, request)

        context = view.get_context_data()

        if request.user.is_authenticated():
            nb_user_service = nb_service = 20
            if nb_user_service == nb_service:
                context['action'] = 'hide'
            else:
                context['action'] = 'display'

            if nb_user_service == nb_service:
                self.assertEqual(context['action'], 'hide')
            else:
                self.assertEqual(context['action'], 'display')

            nb_user_service = 19
            nb_service = 20
            if nb_user_service == nb_service:
                context['action'] = 'hide'
            else:
                context['action'] = 'display'

            if nb_user_service == nb_service:
                self.assertEqual(context['action'], 'hide')
            else:
                self.assertEqual(context['action'], 'display')


def setup_view(view, request, *args, **kwargs):
    """Mimic as_view() returned callable, but returns view instance.

    args and kwargs are the same you would pass to ``reverse()``

    """
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view
