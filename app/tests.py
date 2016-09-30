from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import OfferedService
from app.serializers import OfferedServiceSerializer
from django.contrib.auth.models import User

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


