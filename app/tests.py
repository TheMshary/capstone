from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import OfferedService
from app.serializers import OfferedServiceSerializer
from django.contrib.auth.models import User
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


class SearchTest(APITestCase):

	def setUp(self):
		info = [
			('a', 'a', 1.0, 'pet'),
			('b', 'b', 2.0, 'cleaning'),
			('c', 'c', 2.5, 'real estate'),
			('d', 'd', 3.5, 'pet')
		]

		# make 3 Provider accounts
		for inf in info:
			user = User.objects.create_user(username=inf[0], password=inf[1])
			user.profile.usertype = 'provider'
			user.profile.category = inf[3]
			user.profile.save()
			mommy.make(Rating, profile=user.profile, rate=inf[2])

		# login
		token = Token.objects.get(user__username='a')
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

	def test_search(self):
		url = '/search/'
		data = {
			'search':'pet',
		}
		response = self.client.post(url, data, format='json')

		# self.assertTrue(isinstance(response.data.get(''), Profile))
		self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProviderWorkingOnServicesTest(APITestCase):
	user = None

	def setUp(self):
		# make Provider account
		user = User.objects.create_user(username='e', password='f')
		user.profile.usertype = 'provider'
		user.profile.save()
		self.user = user

		# make 3 Offered Services
		services = mommy.make(Service, providerpk=user.pk, status='active', _quantity=3)
		for service in services:
			mommy.make(OfferedService, service=service)

		# login
		token = Token.objects.get(user__username='e')
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

	def test_get(self):
		url = '/provider/workingon/'
		response = self.client.get(url, format='json')

		count = len(response.data)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(count, 3)


class ProviderRequestedServicesTest(APITestCase):
	user = None

	def setUp(self):
		# make Provider account
		user = User.objects.create_user(username='e', password='f')
		user.profile.usertype = 'provider'
		user.profile.save()
		self.user = user

		# make 3 Offered Services
		services = mommy.make(Service, providerpk=user.pk, status='pending', _quantity=3)
		for service in services:
			mommy.make(OfferedService, service=service)

		# login
		token = Token.objects.get(user__username='e')
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

	def test_get(self):
		url = '/provider/requests/'
		response = self.client.get(url, format='json')

		count = len(response.data)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(count, 3)


class ProviderBidOnServicesTest(APITestCase):
	user = None

	def setUp(self):
		# make Provider account
		user = User.objects.create_user(username='e', password='f')
		user.profile.usertype = 'provider'
		user.profile.save()
		self.user = user

		# make 5 Public Services, two with bids KD4 and KD6
		services = mommy.make(Service, providerpk=user.pk, _quantity=5)
		for service in services[0:3]:
			mommy.make(PublicService, service=service)

		for service in services[3:5]:
			serv = mommy.make(PublicService, service=service)
			mommy.make(Bid, service=serv, bid=4, bidder=user)

		# login
		token = Token.objects.get(user__username='e')
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

	def test_get(self):
		url = '/publicservice/'
		response = self.client.get(url, format='json')

		bidcount = len(response.data.get('bids'))
		feedcount = len(response.data.get('feed'))
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(bidcount, 2)
		self.assertEqual(feedcount, 5)


class ProviderOfferedServicesTest(APITestCase):
	pk = None

	def setUp(self):
		user = User.objects.create_user(username='e', password='f')
		user.profile.usertype = 'provider'
		user.profile.save()
		self.pk = user.pk

		services = mommy.make(Service, providerpk=self.pk, status="available", _quantity=5)
		for serv in services:
			mommy.make(OfferedService, service=serv)

	def test_get(self):
		url = '/providerservices/'
		data = {
			'providerpk':self.pk
		}
		response = self.client.get(url, data, format='json')

		count = len(OfferedService.objects.filter(service__providerpk=self.pk))
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), count)

class ProviderResponseTest(APITestCase):
	service = None

	def setUp(self):
		# make account
		username = 'testname'
		password = 'whatevs'
		usertype = 'seeker'
		user = User.objects.create_user(username=username, password=password)
		user.profile.usertype = usertype
		user.profile.save()

		# login
		token = Token.objects.get(user__username=username)
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

		serv = mommy.make(Service, status="pending")
		offered = mommy.make(OfferedService, service=serv)
		self.service = serv

	def test_accept(self):
		url = '/providerresponse/'
		data = {
			'pk': self.service.pk,
			'response':'accept'
		}
		response = self.client.post(url, data, format='json')
		self.service = Service.objects.get(pk=self.service.pk)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(self.service.status, 'Active')

	def test_decline(self):
		url = '/providerresponse/'
		data = {
			'pk':self.service.pk,
			'response':'decline'
		}
		response = self.client.post(url, data, format='json')
		self.service = Service.objects.get(pk=self.service.pk)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(self.service.status, 'Declined')

	def test_bad_request(self):
		url = '/providerresponse/'
		data = {
			'pk':self.service.pk,
			'response':'kdjgnrekjg'
		}
		response = self.client.post(url, data, format='json')
		self.service = Service.objects.get(pk=self.service.pk)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(self.service.status, 'pending')
		self.assertEqual(response.data.get('msg'), "'response' can be either 'accept' or 'decline', spelt exactly that way.")

class ProviderDoneTest(APITestCase):
	service = None

	def setUp(self):
		# make account
		username = 'testname'
		password = 'whatevs'
		usertype = 'seeker'
		user = User.objects.create_user(username=username, password=password)
		user.profile.usertype = usertype
		user.profile.save()

		# login
		token = Token.objects.get(user__username=username)
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

		serv = mommy.make(Service)
		self.service = serv

	def test_done(self):
		url = '/providerdone/'
		data = {
			'pk':self.service.pk,
		}
		response = self.client.post(url, data, format='json')
		self.service = Service.objects.get(pk=self.service.pk)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(self.service.status, 'Done')


class BidResponseTest(APITestCase):
	accept_bid = None
	decline_bid = None

	def setUp(self):
		# make account
		username = 'testname'
		password = 'whatevs'
		usertype = 'seeker'
		user = User.objects.create_user(username=username, password=password)
		user.profile.usertype = usertype
		user.profile.save()

		# login
		token = Token.objects.get(user__username=username)
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

		serv = mommy.make(Service)
		pub = mommy.make(PublicService, service=serv)
		self.accept_bid = mommy.make(Bid, service=pub, bid=4)
		self.decline_bid = mommy.make(Bid, service=pub, bid=5)

	def test_accept(self):
		url = '/acceptbid/'
		data = {
			'pk':self.accept_bid.pk,
		}
		response = self.client.post(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_decline(self):
		url = '/declinebid/'
		data = {
			'pk':self.decline_bid.pk,
		}
		response = self.client.post(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)

class BidTest(APITestCase):
	servicepk = 0
	title = 'tootle'
	description = 'dyctryptin'
	price = 6
	bid = 7
	bidpk = 0
	user = None

	def setUp(self):
		# make account
		username = 'testname'
		password = 'whatevs'
		usertype = 'provider'
		user = User.objects.create_user(username=username, password=password)
		user.profile.usertype = usertype
		user.profile.save()
		self.user = user
		
		# login
		token = Token.objects.get(user__username=username)
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

		serv = mommy.make(Service, title=self.title, description=self.description, price=self.price)
		pub = mommy.make(PublicService, service=serv)
		bid = mommy.make(Bid, service=pub, bid=3)
		
		self.servicepk = pub.pk
		self.bidpk = bid.pk

	def test_create(self):
		url = '/bid/'
		data = {
			'service': self.servicepk,
			'bid': 5,
			'bidder':self.user.pk
		}

		response = self.client.post(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_create_400(self):
		url = '/bid/'
		data = {
			'pk': self.servicepk,
			'bid': 'a'
		}

		response = self.client.post(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_get(self):
		url = '/bid/'
		data = {
			'pk':self.servicepk,
		}
		response = self.client.get(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_update(self):
		url = '/bid/'
		data = {
			'pk':self.bidpk,
			'service':self.servicepk,
			'bid':self.bid
		}
		response = self.client.put(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_update_400(self):
		url = '/bid/'
		data = {
			'pk':self.bidpk,
			'service':self.servicepk,
			'bid':'sef'
		}
		response = self.client.put(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_update_404(self):
		url = '/bid/'
		data = {
			'pk':242,
			'service':242,
			'bid':self.bid
		}
		response = self.client.put(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_delete(self):
		url = '/bid/'
		data = {
			'pk':self.bidpk,
		}

		res = Bid.objects.filter(service__pk=self.servicepk)
		before = len(res)

		response = self.client.delete(url, data, format='json')

		res = Bid.objects.filter(service__pk=self.servicepk)
		after = len(res)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(before, after+1)

class PublicServiceTest(APITestCase):
	servicepk = 0
	title = "tweetle"
	description = "hehe -scription"
	price = 1337

	def setUp(self):
		# make account
		username = 'testname'
		password = 'whatevs'
		usertype = 'seeker'
		user = User.objects.create_user(username=username, password=password)
		user.profile.usertype = usertype
		user.profile.save()

		# login
		token = Token.objects.get(user__username=username)
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

		serv = mommy.make(Service, title=self.title, description=self.description, price=self.price)
		pub = mommy.make(PublicService, service=serv)
		
		self.servicepk = pub.pk

	def test_create(self):
		url = '/publicservice/'
		data = {
			'service': {
				'title':'some title',
				'description':'some description',
				'price':3.14159265,
			}
		}
		response = self.client.post(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_create_invalid(self):
		url = '/publicservice/'
		data = {
			'service': {
				'title':'some title',
				'description':'some description',
				'price':'qfwe  wefs',
			}
		}
		response = self.client.post(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_get_list(self):
		url = '/publicservice/'
		response = self.client.get(url, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_update(self):
		url = '/publicservice/'
		newdesc = 'this is the new fucking description yo'
		data = {
			'pk':self.servicepk,
			'service':{
				'description':newdesc
			}
		}
		response = self.client.put(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data.get('service').get('description'), newdesc)

	def test_update_invalid(self):
		url = '/publicservice/'
		newprice = 'this is the new fucking price yo'
		data = {
			'pk':self.servicepk,
			'service':{
				'price':newprice
			}
		}
		response = self.client.put(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

	def test_get_detailed_404(self):
		url = '/publicservice/'
		data = {
			'servicepk':'43434'
		}
		response = self.client.get(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_delete(self):
		url = '/publicservice/'
		data = {
			'pk':self.servicepk,
		}
		bids = mommy.make(Bid, _quantity=3)
		publicserv = PublicService.objects.get(pk=self.servicepk)
		publicserv.bid_set = bids

		res = self.client.get(url, format='json')
		before = len(res.data.get('feed'))

		response = self.client.delete(url, data, format='json')

		res = self.client.get(url, format='json')
		after = len(res.data.get('feed'))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(before, after+1)


class OfferedServiceTest(APITestCase):
	servicepk = 0
	title = 'tootle'
	description = 'deezkroptyn'
	price = 5.9

	def setUp(self):
		# make account
		username = 'testname'
		password = 'whatevs'
		usertype = 'provider'
		user = User.objects.create_user(username=username, password=password)
		user.profile.usertype = usertype
		user.profile.save()

		# login
		token = Token.objects.get(user__username=username)
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

		serv = mommy.make(Service, title=self.title, description=self.description, price=self.price)
		offered = mommy.make(OfferedService, service=serv)

		self.servicepk = offered.pk

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

	def test_create_invalid(self):
		url = '/offeredservice/'
		data = {
			'service': {
				'description':'some description here',
				'title':'some title here',
				'price':'a'
			}
		}
		response = self.client.post(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

	def test_update_invalid(self):
		url = '/offeredservice/'
		newprice = 'this is the new fucking description yo'
		data = {
			'servicepk': self.servicepk,
			'service':{
				'price':newprice
			}
		}
		response = self.client.put(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

	# def test_get_detailed_404(self):
	# 	url = '/offeredservice/'
	# 	OfferedService.objects.all().delete()
	# 	Service.objects.all().delete()
	# 	response = self.client.get(url, format='json')

	# 	self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

	def test_request_404(self):
		url = '/request/'
		data = {
			'servicepk':'3425'
		}

		response = self.client.post(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

	def test_delete_404(self):
		url = '/offeredservice/'
		data = {
			'servicepk': '34234',
		}

		response = self.client.delete(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LoginTest(APITestCase):
	seekerusername = "seekername"
	seekerpassword = "seekerpass"

	providerusername = "providername"
	providerpassword = "providerpass"

	def setUp(self):
		# make account
		username = self.seekerusername
		password = self.seekerpassword
		usertype = 'seeker'
		user = User.objects.create_user(username=username, password=password)
		user.profile.usertype = usertype
		user.profile.save()

		# make account
		username = self.providerusername
		password = self.providerpassword
		usertype = 'provider'
		user = User.objects.create_user(username=username, password=password)
		user.profile.usertype = usertype
		user.profile.save()

	def test_signup_username_taken(self):
		url = '/signup/'
		data = {
			'username':self.seekerusername,
			'password':self.seekerpassword,
			'usertype':'seeker'
		}
		response = self.client.post(url, data, format='json')

		self.assertEqual(response.data.get("msg"), 'Username taken.')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_signup_invalid(self):
		url = '/signup/'
		data = {
			'username':'dfghjk',
			'password':self.seekerpassword,
			'usertype':'hgvmh'
		}
		response = self.client.post(url, data, format='json')

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

	def test_token_404(self):
		url = '/login/'
		Token.objects.get(user__username=self.providerusername).delete()
		data = {
			'username':self.providerusername,
			'password':self.providerpassword
		}
		response = self.client.post(url, data, format='json')


		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProfileUpdateTest(APITestCase):
	profile = None
	token = ''

	def setUp(self):
		# make account
		username = 'lolxDxD'
		password = 'haha'
		usertype = 'provider'
		user = User.objects.create_user(username=username, password=password)
		user.profile.usertype = usertype
		user.profile.save()

		# login
		token = Token.objects.get(user__username=username)
		# Include an appropriate 'Authorization:' header on all requests.
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

	def test_update(self):
		url = "/profile/"
		data = {
			'usertype':'seeker',
			"about":"new about"
		}
		response = self.client.put(url, data, HTTP_AUTHORIZATION=self.token)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data.get('about'), 'new about')

	def test_update_400(self):
		url = "/profile/"
		data = {
			'usertype':3,
			"about":6,
			'email':4
		}
		response = self.client.put(url, data, HTTP_AUTHORIZATION=self.token)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_get(self):
		url = '/profile/'
		response = self.client.get(url, HTTP_AUTHORIZATION=self.token)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserTypeTest(APITestCase):
	username = "xDxD"
	password = "lololol!1!11!1!!"
	usertype = "seeker"
	
	def setUp(self):
		# make account
		username = self.username
		password = self.password
		usertype = self.usertype
		user = User.objects.create_user(username=username, password=password)
		user.profile.usertype = usertype
		user.profile.save()

	def test_usertype(self):
		url = "/login/"
		data = {"username":self.username, "password":self.password}
		response = self.client.post(url, data, format='json')

		self.assertEqual(response.data.get('usertype'), self.usertype)


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


























