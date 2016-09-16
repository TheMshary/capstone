import pprint
#============================ DJANGO IMPORTS ============================#
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import render
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.six import BytesIO

#======================== REST FRAMEWORK IMPORTS ========================#
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authtoken.models import Token
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

#============================= APP IMPORTS ==============================#
from app.forms import OfferedServiceForm, UserSignup, UserLogin
from app.models import (
	Profile, 
	Service,
	PublicService, 
	OfferedService, 
	ServiceImage,
	Bid, 
)
from app.serializers import (
	UserSerializer, 
	ServiceImageSerializer,
	ServiceSerializer,
	BidSerializer,
	OfferedServiceSerializer, 
	PublicServiceSerializer, 
	ProfileSerializer, 
)

# TODO:
## BidView doesn't authenticate
## providerpk in OfferedServiceView isn't being automatically assigned
## seekerpk in PublicServiceView isn't being automatically assigned
## the __str__() of OfferedService doesn't work right


# Create your views here.

class ProfileView(APIView):
	"""
	Provider Profile stuff
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		user = request.user
		profile = user.profile
		# serialize profile
		serializer = ProfileSerializer(profile)
		# return serialized data
		return Response(serializer.data, status=status.HTTP_200_OK)

	def put(self, request, format=None):
		# parse the request into JSON. Required?
		# data = JSONParser().parse(request)

		user = request.user
		profile = user.profile

		# serialize the JSON
		serializer = ProfileSerializer(profile, data=request.data)

		# validate and save the serializer, and return the data back - 201 created
		if serializer.is_valid():
			serializer.save()

			return Response(serializer.data, status=status.HTTP_200_OK)

		# JSON is not in valid format, return errors - 400 bad request
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfferedServiceView(APIView):
	"""
	List all Offered Services, or create a new Offered Service
	"""

	authentication_classes = (TokenAuthentication,)
	# permission_classes = (IsAuthenticated,)
	# permission_classes = (AllowAny,)

	@permission_classes((AllowAny,))
	def get(self, request, format=None):

		# get the fucking token shitface


		query_last = request.GET.get('query_last', None)

		if query_last is not None:
			services = OfferedService.objects.all()[:query_last]
		else:
			services = OfferedService.objects.all()
		
		serializer = OfferedServiceSerializer(services, many=True)

		return Response(serializer.data, status=status.HTTP_200_OK)


	@permission_classes((IsAuthenticated,))
	def post(self, request):

		# pp = pprint.PrettyPrinter(indent=4)

		providerpk = request.user.pk
		data = request.data
		data.get("service").update({"providerpk":providerpk})
		# pp.pprint("DATA: %s" % data)
		serializer = OfferedServiceSerializer(data=request.data)

		# validate and save the serializer, and return the data back - 201 created
		if serializer.is_valid():
			serializer.save()

			return Response(serializer.data, status=status.HTTP_201_CREATED)

		# JSON is not in valid format, return errors - 400 bad request
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@permission_classes((IsAuthenticated,))
	def put(self, request, pk):
		service = self._get_object(pk)
		serializer = OfferedServiceSerializer(service, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@permission_classes((IsAuthenticated,))
	def delete(self, request, pk):
		service = self._get_object(pk)
		for image in service.serviceimage_set.all():
			image.delete()
		service.service.delete()
		service.delete()
		return Response(status=status.HTTP_200_OK)

	def _get_object(self, pk):
		try:
			return OfferedService.objects.get(pk=pk)
		except OfferedService.DoesNotExist, e:
			raise Http404


class PublicServiceView(APIView):
	"""
	List all Public Services, or create a new Public Service
	"""

	authentication_classes = (TokenAuthentication,)
	# permission_classes = (IsAuthenticated,)
	# permission_classes = (AllowAny,)

	@permission_classes((AllowAny,))
	def get(self, request, format=None): #pk=None?

		# get the fucking token shitface


		query_last = request.GET.get('query_last', None)

		if query_last is not None:
			services = PublicService.objects.all()[:query_last] #order_by=service.created ??
		else:
			services = PublicService.objects.all()
		
		serializer = PublicServiceSerializer(services, many=True)

		return Response(serializer.data, status=status.HTTP_200_OK)

	@permission_classes((IsAuthenticated,))
	def post(self, request):

		seekerpk = request.user.pk
		data = request.data
		data.get("service").update({"seekerpk":seekerpk})
		serializer = PublicServiceSerializer(data=request.data)

		# validate and save the serializer, and return the data back - 201 created
		if serializer.is_valid():
			serializer.save()

			return Response(serializer.data, status=status.HTTP_201_CREATED)

		# JSON is not in valid format, return errors - 400 bad request
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@permission_classes((IsAuthenticated,))
	def put(self, request, pk):
		service = self._get_object(pk)
		serializer = PublicServiceSerializer(service, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

	@permission_classes((IsAuthenticated,))
	def delete(self, request, pk):
		service = self._get_object(pk)
		for bid in service.bid_set.all():
			bid.delete()
		service.service.delete()
		service.delete()
		return Response(status=status.HTTP_200_OK)

	def _get_object(self, pk):
		try:
			return PublicService.objects.get(pk=pk)
		except PublicService.DoesNotExist, e:
			raise Http404


class BidView(APIView):
	"""
	List all Public Services, or create a new Public Service
	"""
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)
	# permission_classes = (AllowAny,)

	def get(self, request, pk):

		# get the fucking token shitface


		query_last = request.GET.get('query_last', None)

		service = PublicService.objects.get(pk=pk)


		if query_last is not None:
			bid = Bid.objects.all(service=service)[:query_last]
		else:
			bid = Bid.objects.all(service=service)
		
		serializer = BidSerializer(services, many=True)

		return Response(serializer.data)

	# This doesn't work. Authentication here doesn't work. No idea why.
	def post(self, request, pk):

		# service = PublicService.objects.get(pk=pk)
		data = request.data
		data.update({"service":pk})

		serializer = BidSerializer(data=data)

		# validate and save the serializer, and return the data back - 201 created
		if serializer.is_valid():
			serializer.save()

			return Response(serializer.data, status=status.HTTP_201_CREATED)

		# JSON is not in valid format, return errors - 400 bad request
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, pk):
		bid = self._get_object(pk)
		serializer = BidSerializer(bid, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

	def _get_object(self, pk):
		try:
			service = PublicService.objects.get(pk=pk)
			return Bid.objects.get(service=service)
		except PublicService.DoesNotExist, e:
			raise Http404


class ServiceImagesView(APIView):
	"""
	List all Public Services, or create a new Public Service
	"""

	authentication_classes = (TokenAuthentication,)
	# permission_classes = (IsAuthenticated,)
	# permission_classes = (AllowAny,)

	@permission_classes((AllowAny,))
	def get(self, request, pk):

		# get the fucking token shitface


		service = OfferedService.objects.get(pk=pk)

		images = ServiceImage.objects.all(service=service)
		
		serializer = ServiceImageSerializer(images, many=True)

		return Response(serializer.data, status=status.HTTP_200_OK)

	@permission_classes((IsAuthenticated,))
	def post(self, request, pk):

		service = OfferedService.objects.get(pk=pk)
		data = request.data
		data.update({"service":service})

		serializer = ServiceImageSerializer(data=data)

		# validate and save the serializer, and return the data back - 201 created
		if serializer.is_valid():
			serializer.save()

			return Response(serializer.data, status=status.HTTP_201_CREATED)

		# JSON is not in valid format, return errors - 400 bad request
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@permission_classes((IsAuthenticated,))
	def delete(self, request, pk):
		try:
			image = ServiceImage.objects.get(pk=pk)
		except ServiceImage.DoesNotExist, e:
			raise Http404
		image.delete()
		return Response(status=status.HTTP_200_OK)

	def _get_object(self, pk):
		try:
			return ServiceImage.objects.get(pk=pk)
		except ServiceImage.DoesNotExist, e:
			raise Http404


class LogView(APIView):
	"""
	List all services with the logged in user, to show their log.
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(request):
		user = request.user
		query_last = request.GET.get('query_last', None)

		# Hey you! Yes you, Mr. Refactor! Fix this monstrosity!
		if user.profile.usertype == "seeker":
			if query_last is not None:
				services = Service.objects.filter(seekerpk=user.pk)[:query_last]
			else:
				services = Service.objects.filter(seekerpk=user.pk)
		elif user.profile.usertype == "provider":
			if query_last is not None:
				services = Service.objects.filter(providerpk=user.pk)[:query_last]
			else:
				services = Service.objects.filter(providerpk=user.pk)
		else:
			return Response({"msg": "'usertype' is neither seeker nor provider."}, status=status.HTTP_400_BAD_REQUEST)
		
		serializer = BidSerializer(services, many=True)

		return Response(serializer.data, status=status.HTTP_200_OK)

#============================ ACCOUNTS-RELATED ============================#
@api_view(["POST"])
@csrf_exempt
def token_request(request):

	username = request.data.get("username", None)
	user = User.objects.get(username=username)

	token = "NONE"
	try:
		token = Token.objects.get(user=user)
		response_code = status.HTTP_200_OK
	except Exception, e:
		response_code = status.HTTP_404_NOT_FOUND
		token = "- Token not found for user"
	
	ret_string = "Token %s" % token
	return HttpResponse(ret_string, status=response_code)

@api_view(["POST"])
@csrf_exempt
@permission_classes((AllowAny,))
def signup(request):

	try:
		User.objects.get(username=request.data.get("username"))
		return HttpResponse("Username taken.", status=status.HTTP_400_BAD_REQUEST)
	except User.DoesNotExist:
		pass

	serializer = UserSerializer(data=request.data)

	if serializer.is_valid():
		serializer.save()

		return Response(serializer.data, status=status.HTTP_201_CREATED)

	return HttpResponse("Invalid.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@csrf_exempt
def logout_view(request):
	logout(request)
	return HttpResponse("LOGGED OUT", status=status.HTTP_204_NO_CONTENT)





#============================ SHIT WE MAY NEED ============================#

# class OfferedServiceDetailView(APIView):
# 	"""
# 	Retrieve, Update, or Delete a Offered Service instance
# 	"""
# 	def _get_object(self, pk):
# 		try:
# 			print "GETTING PK-%s" % pk
# 			return OfferedService.objects.get(pk=pk)
# 		except OfferedService.DoesNotExist, e:
# 			raise Http404

# 	def get(self, request, pk):
# 		service = self._get_object(pk)
# 		serializer = OfferedServiceSerializer(service)
# 		return Response(serializer.data)

# 	def put(self, request, pk):
# 		service = self._get_object(pk)
# 		serializer = OfferedServiceSerializer(service, data=request.data)
# 		if serializer.is_valid():
# 			serializer.save()
# 			return Response(serializer.data, status=status.HTTP_200_OK)
# 		return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

# 	def delete(self, request, pk):
# 		service = self._get_object(pk)
# 		service.delete()
# 		return Response(status=HTTP_204_NO_CONTENT)
