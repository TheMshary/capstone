from __future__ import unicode_literals

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.conf import settings

from rest_framework.authtoken.models import Token


# Create your models here.

# This is most likely a signal receiver that runs the function whenever a new User is created
# It creates a new Token and associated it with the created User.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        Profile.objects.create(user=instance)

#============================= PROVIDER PROFILE ==============================#

class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	# username = models.CharField(max_length=100)
	usertype = models.CharField(max_length=101, default="seeker") #Make this into choices
	about = models.TextField(null=True, blank=True)
	phone_number = models.CharField(max_length=100, null=True, blank=True)
	email = models.EmailField(null=True, blank=True)
	image = models.ImageField(upload_to="providers", null=True, blank=True)

	rating = models.FloatField(default=0.0)
	country = models.CharField(max_length=100, null=True, blank=True)
	area = models.CharField(max_length=100, null=True, blank=True)
	street_address = models.CharField(max_length=100, null=True, blank=True)

	def __str__(self):
		return self.user.username

#============================= BASE SERVICE MODEL ==============================#

class Service(models.Model):
	title = models.CharField(max_length=100, null=True, blank=True, default="untitled")
	description = models.TextField(default="No description available.")
	price = models.FloatField(default=0.0)
	status = models.CharField(max_length=100, null=True, blank=True, default="pending")	#Make this into choices
	due_date = models.DateTimeField(null=True, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	seekerpk = models.IntegerField(null=True, blank=True)
	providerpk = models.IntegerField(null=True, blank=True)
	# available Service Days/Hours (has default "any time")

	is_special = models.BooleanField(default=False)

	def __str__(self):
		return "%s" % self.title

#============================= SERVICE TYPES ==============================#

class PublicService(models.Model):
	service = models.OneToOneField(Service, null=True)
	category = models.CharField(max_length=1337, default="other")

	def __str__(self):
		return self.service.title


class OfferedService(models.Model):
	service = models.OneToOneField(Service, null=True)
	category = models.CharField(max_length=1337, default="other")

	def __str__(self):
		return self.service.title

#============================= SUPPORT MODELS ==============================#

class ServiceImage(models.Model):
	# image = models.ImageField(upload_to="offered", null=True)
	image = models.TextField(null=True)
	name = models.CharField(max_length=9001, null=True)
	service = models.ForeignKey(OfferedService, null=True)

	def __str__(self):
		return "%s" % self.name


class Bid(models.Model):
	service = models.ForeignKey(PublicService)
	bid = models.IntegerField(default=0.0)
	status = models.CharField(max_length=101, default="pending") #Make this into choices

	def __str__(self):
		return "%s" % self.bid




