import pprint

from django.contrib.auth.models import User

from rest_framework import serializers

from app.models import PredefinedService, ServiceImage
from base64 import b64decode
from django.core.files.base import ContentFile

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('username', 'email', 'password')
		# write_only_fields = ('password',)


class ServiceImageSerializer(serializers.ModelSerializer):

	class Meta:
		model = ServiceImage
		fields = ('image', 'name', 'predefinedservice')


class PredefinedServiceSerializer(serializers.ModelSerializer):
	serviceimage_set = ServiceImageSerializer(many=True)

	class Meta:
		model = PredefinedService
		fields = ('title', 'description', 'price', 'serviceimage_set')

	def create(self, validated_data):
		images_data = validated_data.pop('serviceimage_set')
		service = PredefinedService.objects.create(**validated_data)

		for image_data in images_data:
			ServiceImage.objects.create(predefinedservice=service, **image_data)
			
		return service


