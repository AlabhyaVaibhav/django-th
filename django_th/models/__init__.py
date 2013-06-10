# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

# those 2 lines needs to be here to be able to generate the tables
# even if those classes are not used at all
from .evernote import Evernote

from .rss import Rss


class ServicesActivated(models.Model):

    """
        Services Activated from the admin
        # Create a ServicesActivated
        >>> from django_th.models import ServicesActivated
        >>> name = 'ServiceRss'
        >>> status = True
        >>> auth_required = True
        >>> description = 'RSS Feeds Service'
        >>> service_activated = ServicesActivated.objects.create(name=name, status=status, auth_required=auth_required, description=description)
        >>> service_activated.show()
        'Service Activated ServiceRss True True RSS Feeds Service'
    """
    name = models.CharField(max_length=200, unique=True)
    status = models.BooleanField()
    auth_required = models.BooleanField()
    description = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Services'
        verbose_name_plural = 'Services'

    def show(self):
        return "Service Activated %s %s %s %s" % (self.name, self.status,
                                                  self.auth_required, self.description)

    def __unicode__(self):
        return "%s" % (self.name)


class UserProfile(models.Model):

    """
        Related user to handle his profile
    """
    user = models.OneToOneField(User)


class UserService(models.Model):

    """
        UserService a model to link service and user
        # Create a UserService
        >>> from django.contrib.auth.models import User
        >>> from django_th.models import UserService, ServicesActivated
        >>> user1 = User.objects.get(id=1)
        >>> token = 'foobar123'
        >>> name = ServicesActivated.objects.get(name='ServiceRss')
        >>> user_service = UserService.objects.create(user=user1, token=token, name=name)
        >>> user_service.show()
        'User Service foxmask foobar123 ServiceRss'
    """
    user = models.ForeignKey(User)
    token = models.CharField(max_length=255)
    name = models.ForeignKey(
        ServicesActivated, to_field='name', related_name='+')

    def show(self):
        return "User Service %s %s %s" % (self.user, self.token, self.name)

    def __unicode__(self):
        return "%s" % (self.name)


class TriggerService(models.Model):

    """
        TriggerService
        # Create some Service
        >>> from django.contrib.auth.models import User
        >>> from django_th.models import UserService, TriggerService
        >>> provider1 = UserService.objects.get(pk=1)
        >>> consummer1 = UserService.objects.get(pk=2)
        >>> user1 = User.objects.get(id=1)
        >>> date_created1 = '20130610'
        >>> service1 = TriggerService.objects.create(provider=provider1, \
        consummer=consummer1, description="My First Service", user=user1, \
        date_created=date_created1, status=True)

        # Show them
        >>> service1.show()
        'My Service ServiceRrss ServiceEvernote My First Service foxmask'
    """
    provider = models.ForeignKey(UserService, related_name='+', blank=True)
    consummer = models.ForeignKey(UserService, related_name='+', blank=True)
    description = models.CharField(max_length=200)
    user = models.ForeignKey(User)
    date_created = models.DateField(auto_now_add=True)
    date_triggered = models.DateTimeField(null=True)
    status = models.BooleanField()

    def show(self):
        return "My Service %s %s %s %s" % (self.provider, self.consummer,
                                           self.description, self.user)

    def __unicode__(self):
        return "%s %s " % (self.provider, self.consummer)


def create_user_profile(sender, instance, created, **kwargs):
    """
        function to create the record in the UserProfile model
    """
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
