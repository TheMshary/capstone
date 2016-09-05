import pprint

from django.contrib.auth.models import User

from rest_framework import serializers

from app.models import OfferedService, ServiceImage, Profile
from base64 import b64decode
from django.core.files.base import ContentFile

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('username', 'password')
		# write_only_fields = ('password',)


class ServiceImageSerializer(serializers.ModelSerializer):

	class Meta:
		model = ServiceImage
		fields = ('image', 'name', 'offeredservice')


class OfferedServiceSerializer(serializers.ModelSerializer):
	serviceimage_set = ServiceImageSerializer(many=True)

	class Meta:
		model = OfferedService
		fields = ('title', 'description', 'price', 'serviceimage_set')

	def create(self, validated_data):
		images_data = validated_data.pop('serviceimage_set')
		service = OfferedService.objects.create(**validated_data)

		for image_data in images_data:
			ServiceImage.objects.create(offeredservice=service, **image_data)
			
		return service


class ProfileSerializer(serializers.Serializer):
	about = serializers.CharField(required=False)
	phone_number = serializers.CharField(required=False)
	email = serializers.EmailField(required=False)
	image = serializers.ImageField(required=False)

	rating = serializers.FloatField(required=False)
	country = serializers.CharField(required=False)
	area = serializers.CharField(required=False)
	street_address = serializers.CharField(required=False)

	def update(self, instance, validated_data):
		instance.about = validated_data.get("about", instance.about)
		instance.phone_number = validated_data.get("phone_number", instance.phone_number)
		instance.email = validated_data.get("email", instance.email)
		instance.image = validated_data.get("image", instance.image)
		instance.rating = validated_data.get("rating", instance.rating)
		instance.country = validated_data.get("country", instance.country)
		instance.area = validated_data.get("area", instance.area)
		instance.street_address = validated_data.get("street_address", instance.street_address)

		instance.save()

		return instance














