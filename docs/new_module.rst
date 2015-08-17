===================
Create a new module
===================

Introduction :
==============

You can start a new module by cloning the project `Django Th Dummy <https://github.com/foxmask/django-th-dummy>`_
which is a vanilla django module, ready to be used, after you've replaced the name of the form/model/class we'll see below

Once you've cloned it, rename the folder th_dummy to the name of your choice.

Below we'll keep the name dummy to continue our explanation


Forms :
=======

the form **th_dummy/forms.py** provides 3 forms :

* **DummyForm** a modelForm
* **DummyFormProvider** which extends DummyForm
* **DummyFormConsumer** which extends DummyForm


DummyForm will define the content of our form, our fields our widget etc


Models :
========

the model **th_dummy/models.py** :

.. code-block:: python

    class Dummy(Services):

        # put whatever you need  here
        # eg title = models.CharField(max_length=80)
        # but keep at least this one
        title = models.CharField(max_length=80)
        trigger = models.ForeignKey('TriggerService')

        class Meta:
            app_label = 'django_th'

        def __str__(self):
            return "%s" % (self.name)

        def show(self):
            return "My Dummy %s" % (self.name)


Key points :
------------

* The model is related to TriggerService model
* The model uses the **app_label** to **django_th** meta, so the Trigger Happy will be added the table name


Service class :
===============

at the beginning of the class **ServiceDummy** (from `th_dummy/my_dummy.py`) you will need to import the class of the
third party application

the class `ServiceDummy` will extend `ServiceMgr` we've imported from `django_th.services.services`

This class is composed at least by 2 methods :

process_data :
--------------

we provide the following parms

* token - the token of the service
* trigger_id - the trigger id we handle
* date_triggered - the date of the last trigger

role : grabs the data of the current service to be provided to another

return : a list composed by : `title`, `url`, `content`, and can return also `my_date` a datetime value

save_data :
-----------

we provider the following parms

* token - the token of the service
* trigger_id - the trigger id we handle,
* data - the data to store (title, url, content), provided by a "process_data" of another service

role : save the data to the `ServiceDummy`

return : a boolean True or False, if the save_data worked fine or not

If the service does not save data, it's the case of the module django-th-rss which just provides stuff and save nothing,
you'll put `pass` to save_data as the body of your code

auth and callback :
-------------------
If your service need an authentication, you'll need 2 new functions `auth` and `callback`

* `auth` will trigger the authentication to the third party application, the Oauth process in fact
* `callback` is triggered when the authentication is done and call by the third party application.
At this step the callback function store the oauth token to the dedicated dummy model as follow :

.. code-block:: python

    def callback(self, request):
        ...
        UserService.objects.filter(
            user=request.user,
            name=ServicesActivated.objects.get(name='ServiceDummy')).update(token=token)

The complete code of this class :
---------------------------------

.. code-block:: python

    # coding: utf-8
    # add here the call of any native lib of python like datetime etc.
    #
    # add the python API here if needed
    from external_api import CallOfApi

    # django classes
    from django.conf import settings
    from django.core.urlresolvers import reverse
    from django.utils.log import getLogger

    # django_th classes
    from django_th.services.services import ServicesMgr
    from django_th.models import UserService, ServicesActivated

    """
        handle process with dummy
        put the following in settings.py

        TH_DUMMY = {
            'consumer_key': 'abcdefghijklmnopqrstuvwxyz',
        }

        TH_SERVICES = (
            ...
            'th_dummy.my_dummy.ServiceDummy',
            ...
        )

    """

    logger = getLogger('django_th.trigger_happy')


    class ServiceDummy(ServicesMgr):


        def __init__(self, ):
            self.dummy_instance = external_api.CallOfApi(
                    settings.TH_DUMMY['consumer_key'], token)        

        def read_data(self, token, trigger_id, date_triggered):
            """
                get the data from the service
                :param trigger_id: trigger ID to process
                :param date_triggered: the date of the last trigger
                :type trigger_id: int
                :type date_triggered: datetime
                :return: list of data found from the date_triggered filter
                :rtype: list
            """
            data = list()
            return cache.set('th_dummy_' + str(trigger_id), data)


        def process_data(self, trigger_id):
            """
                get the data from the service
                :param trigger_id: trigger ID to process
            """
            return cache.get('th_dummy_' + str(trigger_id))

        def save_data(self, token, trigger_id, **data):
            """
                let's save the data

                :param trigger_id: trigger ID from which to save data
                :param **data: the data to check to be used and save
                :type trigger_id: int
                :type **data:  dict
                :return: the status of the save statement
                :rtype: boolean
            """
            from th_dummy.models import Dummy
            status = False

            if token and 'link' in data and data['link'] is not None and len(data['link']) > 0:
                # get the data of this trigger
                trigger = Dummy.objects.get(trigger_id=trigger_id)
                # if the external service need we provide
                # our stored token and token secret then I do
                # token_key, token_secret = token.split('#TH#')

                title = ''
                title = (data['title'] if 'title' in data else '')
                    # add data to the external service
                item_id = self.dummy_instance.add(
                    url=data['link'], title=title, tags=(trigger.tag.lower()))

                sentance = str('dummy {} created').format(data['link'])
                logger.debug(sentance)
                status = True
            else:
                logger.critical(
                    "no token or link provided for trigger ID {} ".format(trigger_id))
                status = False
            return status

        def auth(self, request):
            """
                let's auth the user to the Service
            """
            callback_url = 'http://%s%s' % (
                request.get_host(), reverse('dummy_callback'))

            request_token = self.get_request_token()

            # Save the request token information for later
            request.session['oauth_token'] = request_token['oauth_token']
            request.session['oauth_token_secret'] = request_token[
                'oauth_token_secret']

            # URL to redirect user to, to authorize your app
            auth_url_str = '%s?oauth_token=%s&oauth_callback=%s'
            auth_url = auth_url_str % (self.AUTH_URL,
                                       request_token['oauth_token'],
                                       callback_url)

            return auth_url

        def callback(self, request):
            """
                Called from the Service when the user accept to activate it
            """

            try:
                # finally we save the user auth token
                # As we already stored the object ServicesActivated
                # from the UserServiceCreateView now we update the same
                # object to the database so :
                # 1) we get the previous objet
                us = UserService.objects.get(
                    user=request.user,
                    name=ServicesActivated.objects.get(name='ServiceDummy'))
                # 2) Readability API require to use 4 parms consumer_key/secret +
                # token_key/secret instead of usually get just the token
                # from an access_token request. So we need to add a string
                # seperator for later use to slpit on this one
                access_token = self.get_access_token(
                    request.session['oauth_token'],
                    request.session['oauth_token_secret'],
                    request.GET.get('oauth_verifier', '')
                )
                # us.token = access_token.get('oauth_token') + \
                #    '#TH#' + access_token.get('oauth_token_secret')
                us.token = access_token
                # 3) and save everything
                us.save()
            except KeyError:
                return '/'

            return 'dummy/callback.html'

        def get_request_token(self):
            oauth = OAuth1Session(self.consumer_key,
                                  client_secret=self.consumer_secret)
            return oauth.fetch_request_token(self.REQ_TOKEN)

        def get_access_token(self, oauth_token, oauth_token_secret,
                             oauth_verifier):
            # Using OAuth1Session
            oauth = OAuth1Session(self.consumer_key,
                                  client_secret=self.consumer_secret,
                                  resource_owner_key=oauth_token,
                                  resource_owner_secret=oauth_token_secret,
                                  verifier=oauth_verifier)
            oauth_tokens = oauth.fetch_access_token(self.ACC_TOKEN)

            return oauth_tokens