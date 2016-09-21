#============================= CORE IMPORTS =============================#
from __future__ import unicode_literals

#============================ DJANGO IMPORTS ============================#
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.conf import settings

#======================== REST FRAMEWORK IMPORTS ========================#
from rest_framework.authtoken.models import Token


############### CHOICES = (
############### 		(ACTUAL_VALUE_TO_BE_SET_ON_THE_MODEL, HUMAN_READABLE_NAME),
############### 		(ACTUAL_VALUE_TO_BE_SET_ON_THE_MODEL, HUMAN_READABLE_NAME),
############### 		(ACTUAL_VALUE_TO_BE_SET_ON_THE_MODEL, HUMAN_READABLE_NAME),
############### 		(ACTUAL_VALUE_TO_BE_SET_ON_THE_MODEL, HUMAN_READABLE_NAME),
############### 		(ACTUAL_VALUE_TO_BE_SET_ON_THE_MODEL, HUMAN_READABLE_NAME),
############### 	)
############### field_attribute = models.CharField(max_length=LENGTH, choices=CHOICES)

# Create your models here.

# This is most likely a signal receiver that runs the function whenever a new User is created
# It creates a new Token and Profile and associated it with the created User.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        Profile.objects.create(user=instance)

#============================= PROVIDER PROFILE ==============================#

class Profile(models.Model):
	SEEKER = "seeker"
	PROVIDER = "provider"
	USERTYPE_CHOICES = (
		(SEEKER, "Seeker"),
		(PROVIDER, "Provider"),
	)

	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	usertype = models.CharField(max_length=10, choices=USERTYPE_CHOICES, default=SEEKER)
	about = models.TextField(null=True, blank=True)
	phone_number = models.CharField(max_length=100, null=True, blank=True)
	email = models.EmailField(null=True, blank=True)
	image = models.ImageField(upload_to="providers", null=True, blank=True)

	country = models.CharField(max_length=100, null=True, blank=True)
	area = models.CharField(max_length=100, null=True, blank=True)
	street_address = models.CharField(max_length=100, null=True, blank=True)

	def __str__(self):
		return self.user.username


class Rating(models.Model):
	rate = models.FloatField(default=0.0)
	profile = models.ForeignKey(Profile)

	def __str__(self):
		return "%s" % self.rate

#============================= BASE SERVICE MODEL ==============================#

class Service(models.Model):

	AVAILABLE = "available"
	UNAVAILABLE = "unavailable"
	PENDING = "pending"
	ACTIVE = "active"
	DONE = "done"
	DECLINED = "declined"
	CANCELED = "canceled"
	ZOMBIE = "zombie"
	STATUS_CHOICES = (
		(AVAILABLE, "Available"),
		(UNAVAILABLE, "Unavailable"),
		(PENDING, "Pending"),
		(ACTIVE, "Active"),
		(DONE, "Done"),
		(DECLINED, "Declined"),
		(CANCELED, "Canceled"),
		(ZOMBIE, "Zombie"),
	)

	title = models.CharField(max_length=100, null=True, blank=True, default="untitled")
	description = models.TextField(default="No description available.")
	price = models.FloatField(default=0.0)
	status = models.CharField(max_length=100, choices=STATUS_CHOICES, null=True, blank=True, default=PENDING)
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

	PENDING = "pending"
	ACCEPTED = "accepted"
	DECLINED = "declined"
	STATUS_CHOICES = (
		(PENDING, "Pending"),
		(ACCEPTED, "Accepted"),
		(DECLINED, "Declined"),
	)
	service = models.ForeignKey(PublicService)
	bid = models.IntegerField(default=0.0)
	status = models.CharField(max_length=101, default=PENDING)

	def __str__(self):
		return "%s" % self.bid




