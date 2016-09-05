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
from app.models import OfferedService, Profile
from app.serializers import OfferedServiceSerializer, UserSerializer, ProfileSerializer
from app.forms import OfferedServiceForm, UserSignup, UserLogin


# Create your views here.

class Profile(APIView):
	"""
	Provider Profile stuff
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		user = request.user
		profile = Profile.objects.get(user=user)
		# serialize profile
		serializer = ProfileSerializer(profile)
		# return serialized data
		return Response(serializer.data, status=status.HTTP_200_OK)

	def post(self, request, format=None):
		# parse the request into JSON. Required?
		data = JSONParser().parse(request)

		# serialize the JSON
		serializer = ProfileSerializer(data=data)

		# validate and save the serializer, and return the data back - 201 created
		if serializer.is_valid():
			serializer.save()

			return Response(serializer.data, status=status.HTTP_201_CREATED)

		# JSON is not in valid format, return errors - 400 bad request
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfferedServiceList(APIView):
	"""
	List all Offered Services, or create a new Offered Service
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)
	# permission_classes = (AllowAny,)

	def get(self, request, format=None):

		# get the fucking token shitface


		query_last = request.GET.get('query_last', None)

		if query_last is None:
			services = OfferedService.objects.all()
		else:
			services = OfferedService.objects.all()[:query_last]
		
		serializer = OfferedServiceSerializer(services, many=True)

		return Response(serializer.data)


	def post(self, request):
		# parse the request into JSON. Required?
		# data = JSONParser().parse(request)
		data = request.data

		# serialize the JSON
		serializer = OfferedServiceSerializer(data=data)

		# validate and save the serializer, and return the data back - 201 created
		if serializer.is_valid():
			serializer.save()

			return Response(serializer.data, status=status.HTTP_201_CREATED)

		# JSON is not in valid format, return errors - 400 bad request
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OfferedServiceDetail(APIView):
	"""
	Retrieve, Update, or Delete a Offered Service instance
	"""
	def get_object(self, pk):
		try:
			return OfferedService.objects.get(pk=pk)
		except OfferedService.DoesNotExist, e:
			raise Http404

	def get(self, request, pk):
		service = self.get_object(pk)
		serializer = OfferedServiceSerializer(service)
		return Response(serializer.data)

	def put(self, request, pk):
		service = self.get_object(pk)
		serializer = OfferedServiceSerializer(service, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

	def delete(self, request, pk):
		service = self.get_object(pk)
		service.delete()
		return Response(status=HTTP_204_NO_CONTENT)



#============================ MAKE ACCOUNTS AND STUFF ============================#
@api_view(["POST"])
def login_view(request):
	token = Token.objects.get(user=request.user)
	ret_string = "Token %s" % token
	# return HttpResponse(ret_string, status=status.HTTP_200_OK)

	username = request.POST.get('username', None)
	password = request.POST.get('password', None)

	user = authenticate(username=username, password=password)

	if user is not None:
		if user.is_active:
			login(request, user)
			return HttpResponse("LOGGED IN", status=status.HTTP_204_NO_CONTENT)

	return HttpResponse("DID NOT LOG IN", status=status.HTTP_400_BAD_REQUEST)


# class TokenRequest(APIView):

	# authentication_classes = (BasicAuthentication,)
	# permission_classes = (AllowAny,)

def token_request(request):
	# pp = pprint.PrettyPrinter(indent=4)
	# print "REQUEST.POST: "
	# pp.pprint(request.POST)

	data = JSONParser().parse(request)

	username = data.get("username", None)
	user = User.objects.get(username=username)

	# user = request.user
	token = "NONE"

	try:
		token = Token.objects.get(user=user)
		response_code = status.HTTP_200_OK
	except Exception, e:
		response_code = status.HTTP_404_NOT_FOUND
		token = "- Token not found for user"
	
	ret_string = "Token %s" % token
	# login(user)
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




