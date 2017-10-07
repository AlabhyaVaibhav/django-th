# coding: utf-8
from django.db import models
from django_th.models.services import Services


class Reddit(Services):

    """
        reddit model to be adapted for the new service
    """
    # put whatever you need  here
    # eg title = models.CharField(max_length=80)
    # but keep at least this one
    trigger = models.ForeignKey('TriggerService')

    class Meta:
        app_label = 'django_th'
        db_table = 'django_th_reddit'

    def __str__(self):
        return self.name

    def show(self):
        return "My Reddit %s" % self.name
