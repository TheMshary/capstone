import pprint
from base64 import b64decode

from django.contrib.auth.models import User
from django.core.files.base import ContentFile

from rest_framework import serializers

from app.models import OfferedService, ServiceImage, Profile, Service, Bid, PublicService


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('username', 'password')
		# write_only_fields = ('password',)


class ServiceImageSerializer(serializers.ModelSerializer):

	class Meta:
		model = ServiceImage
		fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):

	class Meta:
		model = Service
		fields = '__all__'


class BidSerializer(serializers.ModelSerializer):

	class Meta():
		model = Bid
		fields = '__all__'

	

	# def create(self, validated_data):
	# 	servicepk = validated_data.get("service", None)
	# 	service = Service.objects.get(pk=servicepk)

	# 	bid = validated_data.get("bid", 0.0)
	# 	instance = Bid.objects.create(service=service, bid=bid)

	# 	return instance

	# def update(self, instance, validated_data):
	# 	instance.bid = validated_data.get("bid", instance.bid)
	# 	instance.save()

	# 	return instance


class OfferedServiceSerializer(serializers.ModelSerializer):
	serviceimage_set = ServiceImageSerializer(many=True)
	service = ServiceSerializer()

	class Meta:
		model = OfferedService
		fields = '__all__'

	def create(self, validated_data):
		images_data = validated_data.pop('serviceimage_set')
		service_data = validated_data.pop('service')

		service = Service.objects.create(**service_data)
		offeredservice = OfferedService.objects.create(service=service, **validated_data)

		for image_data in images_data:
			ServiceImage.objects.create(service=offeredservice, **image_data)
			
		return offeredservice

	def update(self, instance, validated_data):
		service = validated_data.get("service")

		instance.service.title = service.get("title", instance.service.title)
		instance.service.description = service.get("description", instance.service.description)
		instance.service.price = service.get("price", instance.service.price)
		instance.service.save()

		instance.category = validated_data.get("category", instance.category)
		instance.save()

		return instance


class PublicServiceSerializer(serializers.ModelSerializer):
	bid_set = BidSerializer(many=True)
	service = ServiceSerializer()

	class Meta:
		model = PublicService
		fields = '__all__'

	def create(self, validated_data):
		service_data = validated_data.pop('service')

		service = Service.objects.create(**service_data)
		publicservice = PublicService.objects.create(service=service, **validated_data)

		return publicservice

	def update(self, instance, validated_data):
		service = validated_data.get("service")

		instance.service.title = service.get("title", instance.service.title)
		instance.service.description = service.get("description", instance.service.description)
		instance.service.price = service.get("price", instance.service.price)
		instance.service.save()

		instance.category = validated_data.get("category", instance.category)
		instance.save()

		return instance


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














