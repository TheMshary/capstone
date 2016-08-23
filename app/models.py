from __future__ import unicode_literals

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.conf import settings

from rest_framework.authtoken.models import Token

# Create your models here.

# @receiver(post_save, sender=User)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)


# This is most likely a signal receiver that runs the function whenever a new User is created
# It creates a new Token and associated it with the created User.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class PredefinedService(models.Model):
	title = models.CharField(max_length=100, null=True, blank=True, default="untitled")
	description = models.TextField(default="No description available.")
	price = models.FloatField(default=0.000)
	# available Service Days/Hours (has default "any time")

	def __str__(self):
		return "%s" % self.title


class ServiceImage(models.Model):
	# image = models.ImageField(upload_to="predefined", null=True)
	image = models.TextField(null=True)
	name = models.CharField(max_length=9001, null=True)
	predefinedservice = models.ForeignKey(PredefinedService, null=True)

	def __str__(self):
		return "%s" % self.name


class ProviderProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	image = models.ImageField(upload_to="providers", null=True)
	username = models.CharField(max_length=100)
	rating = models.FloatField()
	bio = models.TextField()
	phone_number = models.CharField(max_length=20)
	email = models.EmailField()
	address = models.CharField(max_length=100)

	def __str__(self):
		return self.username


