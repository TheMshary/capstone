from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import PredefinedService
from app.serializers import PredefinedServiceSerializer

# Create your tests here.

class PredefinedServiceTests(APITestCase):
	
	def setUp(self):
		predefined_service = PredefinedService.objects.create(title="TEST", description="TESTITY")
		predefined_service.save()

	def test_create_predefinedservice(self):
		"""
		Ensure we can create a new Predefined Service object.
		"""
		data = {'title': 'service title', 'description': 'service description over here...'}
		response = self.client.post("/predefinedservice/", data)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(PredefinedService.objects.all()[1].title, 'service title')
		self.assertEqual(PredefinedService.objects.all()[1].description, 'service description over here...')

	def test_get_predefinedservice(self):
		"""
		Ensure we can create a new Predefined Service object.
		"""
		response = self.client.get("/predefinedservice/")

		groups = PredefinedService.objects.all()
		expected = PredefinedServiceSerializer(groups, many=True)

		self.assertEqual(response.data, expected.data)