#============================= CORE IMPORTS =============================#
import pprint
from base64 import b64decode

#============================ DJANGO IMPORTS ============================#
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.http import Http404

#======================== REST FRAMEWORK IMPORTS ========================#
from rest_framework import serializers

#============================= APP IMPORTS ==============================#
from app.models import OfferedService, ServiceImage, Profile, Service, Bid, PublicService


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('username', 'password')


class ServiceImageSerializer(serializers.ModelSerializer):

	class Meta:
		model = ServiceImage
		fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):

	class Meta:
		model = Service
		fields = '__all__'


class ServiceLogSerializer(serializers.Serializer):

	def to_representation(self, service):
		"""
		When using this serializer to serialize to JSON representation,
		this function returns that JSON.
		"""

		try:
			provider = User.objects.get(pk=service.providerpk).username
		except User.DoesNotExist, e:
			provider = None

		try:
			seeker = User.objects.get(pk=service.seekerpk).username
		except User.DoesNotExist, e:
			seeker = None

		data = {
			'title': service.title,
			'status': service.status,
			'created': service.created,
			'due_date': service.due_date,
			'provider': provider,
			'seeker': seeker,
		}

		try:
			offered = service.offeredservice
			servicedata = {
				"id": offered.pk,
				"type": "offered",
			}
		except OfferedService.DoesNotExist, e:
			try:
				public = service.publicservice
				
				servicedata = {
					"id": public.pk,
					"type": "public",
				}
			except PublicService.DoesNotExist, e:
				raise Http404

		data.update(servicedata)
		return data

class BidSerializer(serializers.ModelSerializer):

	class Meta():
		model = Bid
		fields = '__all__'


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
	bid_set = BidSerializer(required=False,many=True)
	service = ServiceSerializer(required=False)

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
	usertype = serializers.CharField(required=False)

	rating = serializers.FloatField(required=False)
	country = serializers.CharField(required=False)
	area = serializers.CharField(required=False)
	street_address = serializers.CharField(required=False)

	def update(self, instance, validated_data):
		instance.about = validated_data.get("about", instance.about)
		instance.phone_number = validated_data.get("phone_number", instance.phone_number)
		instance.email = validated_data.get("email", instance.email)
		instance.image = validated_data.get("image", instance.image)
		instance.usertype = validated_data.get("usertype", instance.usertype)
		
		instance.rating = validated_data.get("rating", instance.rating)
		instance.country = validated_data.get("country", instance.country)
		instance.area = validated_data.get("area", instance.area)
		instance.street_address = validated_data.get("street_address", instance.street_address)

		instance.save()

		return instance














