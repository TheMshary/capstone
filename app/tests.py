from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import OfferedService
from app.serializers import OfferedServiceSerializer
from django.contrib.auth.models import User
<<<<<<< HEAD
from rest_framework.authtoken.models import Token
from model_mommy import mommy

# Create your tests here.

# class Test(APITestCase):
# 	def setUp(self):

# 	def test_(self):
# 		url = '//'
# 		data = {
# 			,
# 		}
# 		response = self.client.(url, data, format='json')

# 		self.assertEqual(response.status_code, status.HTTP_)

#======================== API TESTS ========================#


class ProviderDoneTest(APITestCase):
	service = None

	def setUp(self):
		url = '/signup/'
		username = 'testname'
		password = 'whatevs'
		usertype = 'seeker'
		data = {
			'username':username,
			'password':password,
			'usertype':usertype
		}
		self.client.post(url, data, format='json')
		token = Token.objects.get(user__username=username)
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

		serv = mommy.make(Service)
		self.service = serv

	def test_done(self):
		url = '/providerdone/%s/' % self.service.pk
		response = self.client.post(url, format='json')
		self.service = Service.objects.get(pk=self.service.pk)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(self.service.status, 'Done')


class BidResponseTest(APITestCase):
	accept_bid = None
	decline_bid = None

	def setUp(self):
		url = '/signup/'
		username = 'testname'
		password = 'whatevs'
		usertype = 'seeker'
		data = {
			'username':username,
			'password':password,
			'usertype':usertype
		}
		self.client.post(url, data, format='json')
		token = Token.objects.get(user__username=username)
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


		serv = mommy.make(Service)
		pub = mommy.make(PublicService, service=serv)
		self.accept_bid = mommy.make(Bid, service=pub, bid=4)
		self.decline_bid = mommy.make(Bid, service=pub, bid=5)

	def test_accept(self):
		url = '/acceptbid/%s/' % self.accept_bid.pk
		response = self.client.post(url, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_decline(self):
		url = '/declinebid/%s/' % self.decline_bid.pk
		response = self.client.post(url, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)

class BidTest(APITestCase):
	servicepk = 0
	title = 'tootle'
	description = 'dyctryptin'
	price = 6
	bid = 7
	bidpk = 0

	def setUp(self):
		url = '/signup/'
		username = 'testname'
		password = 'whatevs'
		usertype = 'seeker'
		data = {
			'username':username,
			'password':password,
			'usertype':usertype
		}
		self.client.post(url, data, format='json')
		token = Token.objects.get(user__username=username)
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


		url2 = '/publicservice/'
		data2 = {
			'service': {
				'title':self.title,
				'description':self.description,
				'price':self.price,
			}
		}
		response = self.client.post(url2, data2, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		self.servicepk = response.data.get('id')

		url3 = '/bid/%s/' % self.servicepk
		data3 = {
			'service':self.servicepk,
			'bid': 3
		}

		response = self.client.post(url3, data3, format='json')
		self.bidpk = response.data.get('id')

	def test_create(self):
		url = '/bid/%s/' % self.servicepk
		data = {
			'service': self.servicepk,
			'bid': 5
		}

		response = self.client.post(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_get(self):
		url = '/bid/%s/' % self.servicepk
		response = self.client.get(url, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_update(self):
		url = '/bid/%s/' % self.bidpk
		data = {
			'service':self.servicepk,
			'bid':self.bid
		}
		response = self.client.put(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_delete(self):
		url = '/bid/%s/' % self.bidpk
		url2 = '/bid/%s/' % self.servicepk

		res = self.client.get(url2, format='json')
		before = len(res.data)

		response = self.client.delete(url, format='json')

		res = self.client.get(url2, format='json')
		after = len(res.data)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(before, after+1)

class PublicServiceTest(APITestCase):
	servicepk = 0
	title = "tweetle"
	description = "hehe -scription"
	price = 1337

	def setUp(self):
		url = '/signup/'
		username = 'testname'
		password = 'whatevs'
		usertype = 'seeker'
		data = {
			'username':username,
			'password':password,
			'usertype':usertype
		}
		self.client.post(url, data, format='json')
		token = Token.objects.get(user__username=username)
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


		url2 = '/publicservice/'
		data2 = {
			'service': {
				'title':self.title,
				'description':self.description,
				'price':self.price,
			}
		}
		response = self.client.post(url2, data2, format='json')

		self.servicepk = response.data.get('id')

	def test_create(self):
		url = '/publicservice/'
		data = {
			'service': {
				'title':'some title',
				'description':'some description',
				'price':3.14152965,
			}
		}
		response = self.client.post(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_get_list(self):
		url = '/publicservice/'
		response = self.client.get(url, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_update(self):
		url = '/publicservice/%s/' % self.servicepk
		newdesc = 'this is the new fucking description yo'
		data = {
			'service':{
				'description':newdesc
			}
		}
		response = self.client.put(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data.get('service').get('description'), newdesc)

	def test_get_detailed(self):
		url = '/publicservice/'
		data = {
			'servicepk':self.servicepk
		}
		response = self.client.get(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data.get('service').get('title'), self.title)
		self.assertEqual(response.data.get('service').get('description'), self.description)
		self.assertEqual(response.data.get('service').get('price'), self.price)

	def test_delete(self):
		url = '/publicservice/%s/' % self.servicepk
		res = self.client.get('/publicservice/', format='json')
		before = len(res.data)

		response = self.client.delete(url, format='json')

		res = self.client.get('/publicservice/', format='json')
		after = len(res.data)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(before, after+1)


class OfferedServiceTest(APITestCase):
	servicepk = 0
	title = 'tootle'
	description = 'deezkroptyn'
	price = 5.9

	def setUp(self):
		url = '/signup/'
		username = 'testname'
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


		url2 = '/offeredservice/'
		data2 = {
			'service': {
				'description':self.description,
				'title':self.title,
				'price':self.price
			}
		}
		response = self.client.post(url2, data2, format='json')
		self.servicepk = response.data.get('id')

	def test_create(self):
		url = '/offeredservice/'
		data = {
			'service': {
				'description':'some description here',
				'title':'some title here',
				'price':5.5
			}
		}
		response = self.client.post(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		# self.servicepk = response.data.get('service').get('pk')

	def test_get_list(self):
		url = '/offeredservice/'
		response = self.client.get(url, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	# def test_get_list_query_last(self):
	# 	url = '/offeredservice/'
	# 	query_last = 3
	# 	data = {
	# 		'query_last':query_last
	# 	}
	# 	response = self.client.get(url, data, format='json')

	# 	self.assertEqual(response.status_code, status.HTTP_200_OK)
	# 	self.assertEqual(len(response.data), query_last)

	def test_update(self):
		url = '/offeredservice/'
		newdesc = 'this is the new fucking description yo'
		data = {
			'servicepk': self.servicepk,
			'service':{
				'description':newdesc
			}
		}
		response = self.client.put(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data.get('service').get('description'), newdesc)

	# def test_get_list_related_to_provider(self):

	# def test_get_list_related_to_provider_query_last(self):

	def test_get_detailed(self):
		url = '/offeredservice/'
		data = {
			'servicepk':self.servicepk
		}
		response = self.client.get(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data.get('service').get('title'), self.title)
		self.assertEqual(response.data.get('service').get('description'), self.description)
		self.assertEqual(response.data.get('service').get('price'), self.price)

	def test_request(self):
		url = '/request/'
		data = {
			'servicepk':self.servicepk
		}

		res = self.client.get('/offeredservice/', format='json')
		before = len(res.data)

		response = self.client.post(url, data, format='json')

		res = self.client.get('/offeredservice/', format='json')
		after = len(res.data)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(before, after-1)

	def test_delete(self):
		url = '/offeredservice/'
		data = {
			'servicepk': self.servicepk,
		}
		res = self.client.get('/offeredservice/', format='json')
		before = len(res.data)

		response = self.client.delete(url, data, format='json')

		res = self.client.get('/offeredservice/', format='json')
		after = len(res.data)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(before, after+1)


class LoginTest(APITestCase):
	seekerusername = "seekername"
	seekerpassword = "seekerpass"

	providerusername = "providername"
	providerpassword = "providerpass"

	def setUp(self):
		url = '/signup/'
		data = {
			'username':self.seekerusername,
			'password':self.seekerpassword,
			'usertype':'seeker'
		}
		response = self.client.post(url, data, format='json')

		url = '/signup/'
		data = {
			'username':self.providerusername,
			'password':self.providerpassword,
			'usertype':'provider'
		}
		response = self.client.post(url, data, format='json')

	def test_seeker(self):
		url = '/login/'
		data = {
			'username':self.seekerusername,
			'password':self.seekerpassword
		}
		response = self.client.post(url, data, format='json')

		user = User.objects.get(username=self.seekerusername)
		token = 'Token %s' % Token.objects.get(user=user).key

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data.get('token'), token)
		self.assertEqual(response.data.get('usertype'), 'seeker')

	def test_provider(self):
		url = '/login/'
		data = {
			'username':self.providerusername,
			'password':self.providerpassword
		}
		response = self.client.post(url, data, format='json')

		user = User.objects.get(username=self.providerusername)
		token = 'Token %s' % Token.objects.get(user=user).key

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data.get('token'), token)
		self.assertEqual(response.data.get('usertype'), 'provider')


class ProfileUpdateTest(APITestCase):
	profile = None
	token = ''

	def setUp(self):
		url = "/signup/"
		data = {
			'username':'lolxDxD',
			"password":"haha",
			'usertype':'provider'
		}
		response = self.client.post(url, data, format='json')
		user = User.objects.get(username='lolxDxD')
		self.profile = user.profile
		self.token = 'Token %s' % Token.objects.get(user=user).key


	def test_update(self):
		url = "/profile/"
		data = {
			'usertype':'seeker',
			"about":"new about"
		}
		response = self.client.put(url, data, HTTP_AUTHORIZATION=self.token)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data.get('about'), 'new about')

	def test_get(self):
		url = '/profile/'
		response = self.client.get(url, HTTP_AUTHORIZATION=self.token)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserTypeTest(APITestCase):
	username = "xDxD"
	password = "lololol!1!11!1!!"
	usertype = "seeker"
	
	def setUp(self):
=======

# Create your tests here.

# class AccountTests(APITestCase):
# 	def test_create_account(self):
# 		"""
# 		Ensure we can create a new account object.
# 		"""
# 		url = reverse('account-list')
# 		data = {'name': 'DabApps'}
# 		response = self.client.post(url, data, format='json')
# 		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
# 		self.assertEqual(Account.objects.count(), 1)
# 		self.assertEqual(Account.objects.get().name, 'DabApps')

class UserTypeTests(APITestCase):
	username = "xDxD"
	password = "lololol!1!11!1!!"
	usertype = "seeker"
	
	def setUp(self):
>>>>>>> master
		url = "/signup/"
		data = {"username":self.username, "password":self.password, "usertype":self.usertype}
		response = self.client.post(url, data, format="json")

	# def test_create_account(self):
	# 	url = "/signup/"
	# 	data = {"username":self.username, "password":self.password, "usertype":self.usertype}
	# 	response = self.client.post(url, data, format="json")

	# 	self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_usertype(self):
		url = "/login/"
		data = {"username":self.username, "password":self.password}
		response = self.client.post(url, data, format='json')

		self.assertEqual(response.data.get('usertype'), self.usertype)


<<<<<<< HEAD
#======================== MODEL TESTS ========================#

from app.models import *

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
		self.rating = Rating.objects.create(profile=profile)

	def test_whatever_creation(self):
		w = self.rating
		self.assertTrue(isinstance(w, Rating))
		self.assertEqual(w.__unicode__(), w.rate)		# this shit is bizarre as fuck (it's not, I just don't get Python?)

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
		self.assertEqual(w.__unicode__(), w.bid)


#======================== SERIALIZER TESTS ========================#

from app.serializers import *

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




























=======
# class OfferedServiceTests(APITestCase):
	
# 	def setUp(self):
# 		offered_service = OfferedService.objects.create(title="TEST", description="TESTITY")
# 		offered_service.save()

# 	def test_create_offeredservice(self):
# 		"""
# 		Ensure we can create a new Predefined Service object.
# 		"""
# 		data = {'title': 'service title', 'description': 'service description over here...'}
# 		response = self.client.post("/offeredservice/", data)

# 		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
# 		self.assertEqual(OfferedService.objects.all()[1].title, 'service title')
# 		self.assertEqual(OfferedService.objects.all()[1].description, 'service description over here...')

# 	def test_get_offeredservice(self):
# 		"""
# 		Ensure we can create a new Predefined Service object.
# 		"""
# 		response = self.client.get("/offeredservice/")

# 		groups = OfferedService.objects.all()
# 		expected = OfferedServiceSerializer(groups, many=True)

# 		self.assertEqual(response.data, expected.data)
>>>>>>> master


