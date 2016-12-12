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
        profile = Profile.objects.create(user=instance)
        Rating.objects.create(profile=profile)

#============================= PROVIDER PROFILE ==============================#

class Profile(models.Model):
	CLEANING = 'cleaning'
	FOOD = 'food'
	ERRANDS = 'errands'
	PET = 'pet'
	REAL_ESTATE = 'real estate'
	BEAUTY = 'beauty'
	OTHER = 'other'
	CATEGORY_CHOICES = (
		(CLEANING, 'Cleaning'),
		(FOOD, 'Food'),
		(ERRANDS, 'Errands'),
		(PET, 'Pet'),
		(REAL_ESTATE, 'Real Estate'),
		(BEAUTY, 'Beauty'),
		(OTHER, 'Other'),
	)

	SEEKER = "seeker"
	PROVIDER = "provider"
	USERTYPE_CHOICES = (
		(SEEKER, "Seeker"),
		(PROVIDER, "Provider"),
	)

	created = models.DateTimeField(auto_now_add=True, null=True)
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	usertype = models.CharField(max_length=10, choices=USERTYPE_CHOICES, default=SEEKER)
	about = models.TextField(null=True, blank=True)
	phone_number = models.CharField(max_length=100, null=True, blank=True)
	email = models.EmailField(null=True, blank=True)
	image = models.ImageField(upload_to="providers", null=True, blank=True)

	country = models.CharField(max_length=100, null=True, blank=True)
	area = models.CharField(max_length=100, null=True, blank=True)
	street_address = models.CharField(max_length=100, null=True, blank=True)
	category = models.CharField(max_length=1337, choices=CATEGORY_CHOICES, default=OTHER)

	def __unicode__(self):
		return self.user.username


class Rating(models.Model):
	rate = models.FloatField(default=0.0)
	profile = models.OneToOneField(Profile)

	def __unicode__(self):
		return '%s' % self.rate

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
	due_date = models.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS, null=True, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	seekerpk = models.IntegerField(null=True, blank=True)
	providerpk = models.IntegerField(null=True, blank=True)

	is_special = models.BooleanField(default=False)

	def __unicode__(self):
		return "%s" % self.title

#============================= SERVICE TYPES ==============================#

class PublicService(models.Model):
	CLEANING = 'cleaning'
	FOOD = 'food'
	ERRANDS = 'errands'
	PET = 'pet'
	REAL_ESTATE = 'real estate'
	BEAUTY = 'beauty'
	OTHER = 'other'
	CATEGORY_CHOICES = (
		(CLEANING, 'Cleaning'),
		(FOOD, 'Food'),
		(ERRANDS, 'Errands'),
		(PET, 'Pet'),
		(REAL_ESTATE, 'Real Estate'),
		(BEAUTY, 'Beauty'),
		(OTHER, 'Other'),
	)

	service = models.OneToOneField(Service, null=True)
	category = models.CharField(max_length=1337, choices=CATEGORY_CHOICES, default=OTHER)

	def __unicode__(self):
		return self.service.title


class OfferedService(models.Model):
	CLEANING = 'cleaning'
	FOOD = 'food'
	ERRANDS = 'errands'
	PET = 'pet'
	REAL_ESTATE = 'real estate'
	BEAUTY = 'beauty'
	OTHER = 'other'
	CATEGORY_CHOICES = (
		(CLEANING, 'Cleaning'),
		(FOOD, 'Food'),
		(ERRANDS, 'Errands'),
		(PET, 'Pet'),
		(REAL_ESTATE, 'Real Estate'),
		(BEAUTY, 'Beauty'),
		(OTHER, 'Other'),
	)

	# SATURDAY = "saturday"
	# SUNDAY = "sunday"
	# MONDAY = "monday"
	# TUESDAY = "tuesday"
	# WEDNESDAY = "wednesday"
	# THURSDAY = "thursday"
	# FRIDAY = "friday"
	# STATUS_CHOICES = (
	# 	(SATURDAY, "Saturday"),
	# 	(SUNDAY, "Sunday"),
	# 	(MONDAY, "Monday"),
	# 	(TUESDAY, "Tuesday"),
	# 	(WEDNESDAY, "Wednesday"),
	# 	(THURSDAY, "Thursday"),
	# 	(FRIDAY, "Friday"),
	# )

	service = models.OneToOneField(Service, null=True)
	category = models.CharField(max_length=1337, choices=CATEGORY_CHOICES, default=OTHER)
	
	from_datetime = models.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS, default="0-0-0 0:0")
	to_datetime = models.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS, default="0-0-0 0:0")
	
	# # From this hour at this day
	# weekday_from = models.IntegerField(choices=WEEKDAYS)
	# from_hour = models.IntegerField(choices=range(1,25))

	# # To this hour at this day
 #    weekday_to = models.IntegerField(choices=WEEKDAYS)
 #    to_hour = models.IntegerField(choices=range(1,25))

	def __unicode__(self):
		return self.service.title

#============================= SUPPORT MODELS ==============================#

class ServiceImage(models.Model):
	image = models.ImageField(upload_to="offered", null=True)
	name = models.CharField(max_length=9001, null=True)
	service = models.ForeignKey(OfferedService, null=True)
	created = models.DateTimeField(auto_now_add=True, null=True)

	def __unicode__(self):
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
	bid = models.IntegerField(default=0)
	bidder = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
	status = models.CharField(max_length=101,choices=STATUS_CHOICES, default=PENDING)
	created = models.DateTimeField(auto_now_add=True, null=True)

	def __unicode__(self):
		return "%s" % self.bid




