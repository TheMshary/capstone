from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import OfferedService
from app.serializers import OfferedServiceSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from model_mommy import mommy
from app.serializers import *

#======================== SERIALIZER TESTS ========================#


class OfferedServiceSerializerModelTest(TestCase):
	def test_valid_and_update(self):
		serv = mommy.make(Service)
		w = mommy.make(OfferedService, service=serv)
		data = {
			'service': {
				'title': w.service.title,
				'description': w.service.description,
				'price': w.service.price,
			},
		}
		serializer = OfferedServiceSerializer(data=data)
		self.assertTrue(serializer.is_valid())
		saved = serializer.save()
		self.assertTrue(isinstance(saved, OfferedService))

		# update
		data.update({
			'service': {
				'title': 'new title',
			},
		})
		serializer = OfferedServiceSerializer(saved, data=data)
		self.assertTrue(serializer.is_valid())
		saved = serializer.save()
		self.assertTrue(isinstance(saved, OfferedService))

	def test_invalid(self):
		serv = mommy.make(Service)
		w = mommy.make(OfferedService, service=serv)
		data = {
			'service': {
				'title': w.service.title,
				'description': '',
				'price': '',
			},
		}
		serializer = OfferedServiceSerializer(data=data)
		self.assertFalse(serializer.is_valid())

class PublicServiceSerializerTest(TestCase):
	def test_valid_and_update(self):
		serv = mommy.make(Service)
		w = mommy.make(PublicService, service=serv)
		data = {
			'service': {
				'title': w.service.title,
				'description': w.service.description,
				'price': w.service.price,
			},
		}
		serializer = PublicServiceSerializer(data=data)
		self.assertTrue(serializer.is_valid())
		saved = serializer.save()
		self.assertTrue(isinstance(saved, PublicService))

		# update
		data.update({
			'service': {
				'title': 'new title',
			},
		})
		serializer = PublicServiceSerializer(saved, data=data)
		self.assertTrue(serializer.is_valid())
		saved = serializer.save()
		self.assertTrue(isinstance(saved, PublicService))

	def test_invalid(self):
		serv = mommy.make(Service)
		w = mommy.make(PublicService, service=serv)
		data = {
			'service': {
				'title': w.service.title,
				'description': '',
				'price': '',
			},
		}
		serializer = PublicServiceSerializer(data=data)
		self.assertFalse(serializer.is_valid())

class SeekerLogSerializerTest(APITestCase):
	services = []

	def setUp(self):
		url = '/signup/'
		username = 'testname'
		password = 'whatevs'
		data = {
			'username':username,
			'password':password,
			'usertype':'seeker'
		}
		self.client.post(url, data, format='json')
		token = Token.objects.get(user__username=username)
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
		user = User.objects.get(username=username)
		self.services = mommy.make(Service, seekerpk=user.pk, _quantity=10)

	def test_log(self):
		url = '/log/'
		for service in self.services:
			mommy.make(PublicService, service=service)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_log_fail(self):
		url = '/log/'
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ProviderLogSerializerTest(APITestCase):
	services = []

	def setUp(self):
		url = '/signup/'
		username = 'testname2'
		password = 'whatevs'
		data = {
			'username':username,
			'password':password,
			'usertype':'provider'
		}
		self.client.post(url, data, format='json')
		token = Token.objects.get(user__username=username)
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
		user = User.objects.get(username=username)

		self.services = mommy.make(Service, providerpk=user.pk, _quantity=10)
		for service in self.services:
			mommy.make(OfferedService, service=service)

	def test_log(self):
		url = '/log/'
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

class FailLogSerializerTest(APITestCase):
	services = []

	def setUp(self):
		username = 'testname2'
		password = 'whatevs'

		user = User.objects.create_user(username=username, password=password)
		token = Token.objects.get(user=user)
		# Profile.objects.create(user=user, usertype='prcovider')
		user.profile.usertype = 'prcovider'
		user.profile.save()
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

		# self.services = mommy.make(Service, providerpk=user.pk, _quantity=10)
		# for service in self.services:
			# mommy.make(OfferedService, service=service)

	def test_log(self):
		url = '/log/'
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(response.data.get('msg'), "'usertype' is neither seeker nor provider.")

class PublicServiceProviderBidSerializerTest(TestCase):
	bid = None

	def setUp(self):
		url = '/signup/'
		username = 'testname3'
		password = 'whatevs'
		data = {
			'username':username,
			'password':password,
			'usertype':'provider'
		}
		response = self.client.post(url, data, format='json')

		provider = User.objects.get(username=username)

		service = mommy.make(PublicService, service=mommy.make(Service))
		self.bid = mommy.make(Bid, service=service, bidder=provider)

	def test_valid(self):
		serializer = PublicServiceProviderBidSerializer(self.bid)

		self.assertEqual(serializer.data.get('bid'), self.bid.bid)

