from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import OfferedService
from app.serializers import OfferedServiceSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from model_mommy import mommy
from app.models import *

#======================== MODEL TESTS ========================#


class ProfileTest(TestCase):
	profile = None

	def setUp(self, username="tsty", password="psst"):
		self.profile = User.objects.create_user(username=username, password=password).profile

	def test_whatever_creation(self):
		w = self.profile
		self.assertTrue(isinstance(w, Profile))
		self.assertEqual(w.__unicode__(), w.user.username)

class RatingTest(TestCase):
	rating = None

	def setUp(self, username="tsty", password="psst"):
		profile = User.objects.create_user(username=username, password=password).profile
		self.rating = profile.rating

	def test_whatever_creation(self):
		w = self.rating
		self.assertTrue(isinstance(w, Rating))

class ServiceTest(TestCase):
	service = None

	def setUp(self, title="tsty", description="psst", price=5):
		self.service = Service.objects.create(title=title, description=description, price=price)

	def test_whatever_creation(self):
		w = self.service
		self.assertTrue(isinstance(w, Service))
		self.assertEqual(w.__unicode__(), w.title)

class PublicServiceModelTest(TestCase):
	publicservice = None

	def setUp(self, title="tsty", description="psst", price=5):
		service = Service.objects.create(title=title, description=description, price=price)
		self.publicservice = PublicService.objects.create(service=service)

	def test_whatever_creation(self):
		w = self.publicservice
		self.assertTrue(isinstance(w, PublicService))
		self.assertEqual(w.__unicode__(), w.service.title)

class OfferedServiceModelTest(TestCase):
	offeredservice = None

	def setUp(self, title="tsty", description="psst", price=5):
		service = Service.objects.create(title=title, description=description, price=price)
		self.offeredservice = OfferedService.objects.create(service=service)

	def test_whatever_creation(self):
		w = self.offeredservice
		self.assertTrue(isinstance(w, OfferedService))
		self.assertEqual(w.__unicode__(), w.service.title)

class ServiceImageModelTest(TestCase):
	image = None

	def setUp(self, name="name.png"):
		self.image = ServiceImage.objects.create(name=name)

	def test_whatever_creation(self):
		w = self.image
		self.assertTrue(isinstance(w, ServiceImage))
		self.assertEqual(w.__unicode__(), w.name)

class BidModelTest(TestCase):
	bid = None

	def setUp(self, name="name.png"):
		baseservice = Service.objects.create(title="title", description="descri", price=8)
		service = PublicService.objects.create(service=baseservice)
		self.bid = Bid.objects.create(service=service)

	def test_whatever_creation(self):
		w = self.bid
		self.assertTrue(isinstance(w, Bid))
		self.assertEqual("%s"%w.__unicode__(), "%s"%w.bid)


