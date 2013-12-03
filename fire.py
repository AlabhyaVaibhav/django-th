#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import datetime
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_th.settings")
from django_th.services import default_provider
from django_th.models import TriggerService
from django.utils.log import getLogger

# create logger
logger = getLogger('django_th.trigger_happy')


# todo
# 1) abstract the ".published" properties or add it to each service


def go():
    """
        run the main process
    """
    trigger = TriggerService.objects.filter(status=True)
    if trigger:
        for service in trigger:
            # flag to know if we have to udapte
            to_update = False
            # counting the new data to store to display them in the log
            count_new_data = 0
            # provider - the service that offer datas
            service_name = str(service.provider.name)
            service_provider = default_provider.get_service(service_name)

            # consummer - the service which uses the datas
            service_name = str(service.consummer.name)
            service_consummer = default_provider.get_service(service_name)

            # check if the service has already been triggered
            if service.date_triggered is None:
                logger.debug("first run for %s => %s " % (str(
                    service.provider.name), str(service.consummer.name)))
                to_update = True
            # run run run
            else:
                # 1) get the datas from the provider service
                datas = getattr(service_provider, 'process_data')(**service)
                consummer = getattr(service_consummer, 'save_data')

                published = ''
                # 2) for each one
                for data in datas:
                    # let's try to determine the date contained in the data, otherwise
                    # we'll return the date_triggered of the current service
                    published = to_datetime(data, service.date_triggered)

                    # 3) check if the previous trigger is older than the
                    # date of the data we retreived
                    # if yes , process the consummer
                    date_triggered = datetime.datetime.strptime(
                        str(service.date_triggered)[:-6], '%Y-%m-%d %H:%M:%S')

                    if date_triggered is not None and published is not None and \
                            published >= date_triggered:

                        logger.info(
                            "date %s >= date triggered %s title %s", published, date_triggered, data.title)

                        consummer(
                            service.consummer.token, service.id, **data)

                        to_update = True
                        count_new_data += 1
                    # otherwise do nothing
                    else:
                        logger.debug(
                            "data outdated skiped : [%s] %s", published, data.title)
            # update the date of the trigger
            if to_update:
                logger.info(
                    "user: %s - provider: %s - consummer: %s - %s = %s new data", service.user,
                    service.provider.name, service.consummer.name, service.description, count_new_data)
                update_trigger(service)
            else:
                logger.info(
                    "user: %s - provider: %s - consummer: %s - %s nothing new",
                    service.user, service.provider.name, service.consummer.name, service.description)
    else:
        print "No trigger set by any user"


def update_trigger(service):
    """
        update the date when occurs the trigger
    """
    trigger = TriggerService.objects.get(id=service.id)
    if trigger:
        its_now = datetime.datetime.now()
        triggered = datetime.datetime.fromtimestamp(
            time.mktime(its_now.timetuple()))
        trigger.date_triggered = triggered
        trigger.save()


def to_datetime(data, default_date):
    """
        convert Datetime 9-tuple to the date and time format
        feedparser provides this 9-tuple
    """
    # set a default date and time in case none of the expected
    # xml properties was here
    my_date_time = default_date
    if 'published_parsed' in data:
        my_date_time = datetime.datetime.fromtimestamp(
            time.mktime(data.published_parsed))
    elif 'updated_parsed' in data:
        my_date_time = datetime.datetime.fromtimestamp(
            time.mktime(data.updated_parsed))

    return my_date_time


def main():
    default_provider.load_services()
    # let's go
    go()

if __name__ == "__main__":

    main()
