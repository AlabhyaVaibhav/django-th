.. image:: https://drone.io/github.com/foxmask/django-th/status.png
    :target: https://drone.io/github.com/foxmask/django-th
    :alt: DroneIo Status


.. image:: https://travis-ci.org/foxmask/django-th.svg?branch=master
    :target: https://travis-ci.org/foxmask/django-th
    :alt: Travis Status

.. image:: https://readthedocs.org/projects/trigger-happy/badge/?version=latest
    :target: https://readthedocs.org/projects/trigger-happy/?badge=latest
    :alt: Documentation status

.. image:: https://pypip.in/version/django-th/badge.svg
    :target: https://pypi.python.org/pypi/django-th/
    :alt: Latest version

.. image:: https://pypip.in/py_versions/django-th/badge.svg
    :target: https://pypi.python.org/pypi/django-th/
    :alt: Supported Python versions

.. image:: https://pypip.in/license/django-th/badge.svg
    :target: https://pypi.python.org/pypi/django-th/
    :alt: License


====================
Django Trigger Happy
====================

Automatically share data between popular services you use on the web.
And instead of giving your credentials to them, become the owner of yours !

For example a new RSS item is published, django-trigger-happy will be able to 
automatically create a note on your Evernote account or create a bookmark to
your own Readability or Pocket account and so on

.. image:: http://trigger-happy.eu/static/th_esb.png


Description
===========

The goal of this project is to be independant from any other solution like 
IFTTT, CloudWork or others.

Thus you could host your own solution and manage your own triggers without 
depending any non-free solution.

With this project you can host triggers for you.

All you need is to have a hosting provider (or simply your own server ;) )
who permits to use a manager of tasks like "cron" and, of course Python.

Requirements
============

* Python 3.4.x
* `Django <https://pypi.python.org/pypi/Django/>`_ >= 1.8
* `Celery <http://www.celeryproject.org/>` == 3.1.18
* `django-th-rss <https://github.com/foxmask/django-th-rss>`_ == 0.3.0
* `django-th-pocket <https://github.com/foxmask/django-th-pocket>`_ == 0.2.0
* `django-js-reverse <https://pypi.python.org/pypi/django-js-reverse/>`_ == 0.3.3
* `django-redis-cache <https://pypi.python.org/pypi/django-redis-cache/>` == 0.13.1
* `django-redisboard <https://pypi.python.org/pypi/django-redisboard/>` == 1.2.0

Installation
============

To get the project up and running, from your virtualenv, do:

.. code:: system
    
    git clone https://github.com/foxmask/django-th.git
    

To install the required modules, do:

.. code:: system

    pip install -r https://raw.githubusercontent.com/foxmask/django-th/master/requirements.txt

and at least :

.. code:: system
    
    cd django-th 
    python manage.py syncdb
    python manage.py runserver
    

to startup the database

Parameters
==========

As usual you will setup the database parameters.

Important parts are the settings of the available services :

settings.py 
-----------

add the module django_th to the INSTALLED_APPS


.. code:: python

   INSTALLED_APPS = (
        ...
        'formtools',
        'django_th', 
        'th_rss',
        'django_js_reverse',


then complet with its companion

.. code:: python

        'pocket',     #if you own your own pocket account
        'th_pocket',  #if you own your own pocket account



TH_SERVICES
~~~~~~~~~~~

TH_SERVICES is a list of the services we, like for example,  

.. code:: python

    TH_SERVICES = (
        'th_rss.my_rss.ServiceRss',
        'th_pocket.my_pocket.ServicePocket',
    )


urls.py
-------

.. code:: python

    from django.conf.urls import patterns, include, url
    from django.contrib import admin

    urlpatterns = patterns('',
         # Examples:
         # url(r'^$', 'th.views.home', name='home'),
         # url(r'^blog/', include('blog.urls')),
  
         url(r'^admin/', include(admin.site.urls)),
         url(r'', include('django_th.urls')),
    )


CACHE 
~~~~~

For each TriggerHappy component, define one cache like below 

.. code:: python

    # RSS Cache
    'th_rss':
    {
        'TIMEOUT': 500,
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "127.0.0.1:6379",
        "OPTIONS": {
            "DB": 2,
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
        }
    },

    # Twitter Cache
    'th_twitter':
    {
        'TIMEOUT': 500,
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "127.0.0.1:6379",
        "OPTIONS": {
            "DB": 3,
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
        }
    },



Setting up : Administration
===========================

once the module is installed, go to the admin panel and activate the service you want. 
Currently there are 4 services, RSS, Evernote, Pocket and Readability.

All you can decide here is to tell if the service requires an external authentication or not.


.. image:: http://foxmask.info/public/trigger_happy/th_admin_pocket_activated.png

Once they are activated....

.. image:: http://foxmask.info/public/trigger_happy/admin_service_list.png

... User can use them


Usage :
=======

Activating services : 
---------------------

The user activates the service for their own need. If the service requires an external authentication, he will be redirected to the service which will ask him the authorization to acces the user's account. 
Once it's done, goes back to django-trigger-happy to finish and record the "auth token".

.. image:: http://foxmask.info/public/trigger_happy/public_services_activated.png

Using the activated services :
------------------------------

a set of 3 pages will ask to the user information that will permit to trigger data from a service "provider" to a service "consummer".

For example : 

* page 1 : the user gives a RSS feed
* page 2 : the user gives the name of the notebook where notes will be stored and a tag if he wants
* page 3 : the user gives a description


Fire the Triggers :
===================

Here are the available management commands :

.. code:: python

    Available subcommands:

    [django_th]
        fire_th


To start handling the queue of triggers you/your users configured, just set the management commands fire_th in a crontab or any other scheduler solution of your choice.

.. code:: python

    manage.py fire_th             # will the enchain both read and publish
    manage.py fire_read_data      # will get the data from any service and put them in cache
    manage.py fire_publish_data   # will read the data from the cache and put them to another service

Also : Keep in mind to avoid to set a too short duration between 2 run to avoid to be blocked by the externals services (by their rate limitation) you/your users want to reach.


Complete Documentation
======================

http://trigger-happy.readthedocs.org/


Blog posts :
============

You can find all details of all existing services of the blog :
http://www.foxmask.info/tag/TriggerHappy
