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
from rest_framework import status, permissions
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authtoken.models import Token
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

#============================= APP IMPORTS ==============================#
from app.models import PredefinedService
from app.serializers import PredefinedServiceSerializer, UserSerializer
from app.forms import PredefinedServiceForm, UserSignup, UserLogin


# Create your views here.

class PredefinedServiceList(APIView):
	"""
	List all Predefined Services, or create a new Predefined Service
	"""

	# authentication_classes = (TokenAuthentication, BasicAuthentication)
	# permission_classes = (permissions.IsAuthenticated,)
	# authentication_classes = ()
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):

		query_last = request.GET.get('query_last', None)

		if query_last is None:
			services = PredefinedService.objects.all()
		else:
			services = PredefinedService.objects.all()[:query_last]


		serializer = PredefinedServiceSerializer(services, many=True)

		return Response(serializer.data)


	def post(self, request):
		# parse the request into JSON. Required?
		data = JSONParser().parse(request)

		# serialize the JSON
		serializer = PredefinedServiceSerializer(data=data)

		# validate and save the serializer, and return the data back - 201 created
		if serializer.is_valid():
			serializer.save()

			return Response(serializer.data, status=status.HTTP_201_CREATED)

		# JSON is not in valid format, return errors - 400 bad request
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PredefinedServiceDetail(APIView):
	"""
	Retrieve, Update, or Delete a Predefined Service instance
	"""
	def get_object(self, pk):
		try:
			return PredefinedService.objects.get(pk=pk)
		except PredefinedService.DoesNotExist, e:
			raise Http404

	def get(self, request, pk):
		service = self.get_object(pk)
		serializer = PredefinedServiceSerializer(service)
		return Response(serializer.data)

	def put(self, request, pk):
		service = self.get_object(pk)
		serializer = PredefinedServiceSerializer(service, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
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


@api_view(["POST"])
@csrf_exempt
def logout_view(request):
	logout(request)
	return HttpResponse("LOGGED OUT", status=status.HTTP_204_NO_CONTENT)


class TokenRequest(APIView):

	authentication_classes = (BasicAuthentication,)
	permission_classes = (permissions.AllowAny,)

	def post(self, request):
		pp = pprint.PrettyPrinter(indent=4)
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
# @csrf_exempt
# @permission_classes((permissions.IsAuthenticated,))
# @authentication_classes((BasicAuthentication,))
def token_request(request):
	# user = request.user
	data = JSONParser().parse(request)

	username = data.get("username", "weird shit happening")
	print "POST['username'] -> %s" % username
	user = User.objects.get(username=username)

	token = "NONE"

	# if user.is_authenticated():
	token = Token.objects.get(user=user)
	# 	response_code = status.HTTP_200_OK
	# else:
	# 	response_code = status.HTTP_401_UNAUTHORIZED
	
	ret_string = "Token %s" % token
	return HttpResponse(ret_string, status=200)#response_code)

# header input
# query input
# URL input
# --
# 
@api_view(["POST"])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def signup(request):
	# response = HttpResponse()
	
	# data = JSONParser().parse(request)
	
	serializer = UserSerializer(data=request.data)
	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)

	return HttpResponse("Probably didn't work....", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#============================ OLD SHIT ============================#

# @api_view(["POST"])
# @authentication_classes((BasicAuthentication,))
# @permission_classes((permissions.IsAuthenticated,))
def test(request):
	# return HttpResponse("REQUEST: ", request)
	return render(request, "main.html", {})




def test_delete(request):
	Test.objects.all().delete()
	return HttpResponseRedirect("/")

def api_test(request):
	return HttpResponse("It works!")

@api_view(["GET"])
def api_test_json(request):
	try:
		test = Test.objects.all()
	except Test.DoesNotExist:
		return HttpResponse("no m8", status=status.HTTP_404_NOT_FOUND)

	if request.method == 'GET':
		serializer = TestSerializer(test, many=True)
		return Response(serializer.data)

@api_view(["GET", "POST"])
@csrf_exempt
def predefinedservice(request):
	"""
	List all code snippets, or create a new snippet.
	"""
	if request.method == 'GET':
		predefinedservices = PredefinedService.objects.all()
		serializer = PredefinedServiceSerializer(predefinedservices, many=True)
		print Response(serializer.data)
		return Response(serializer.data)

	elif request.method == 'POST':
		serializer = PredefinedServiceSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
@csrf_exempt
def image_test(request):
	print "REQUEST: ", request
	print "REQUEST DATA: ", request.data

	return HttpResponse("HAHA")
	if request.method == "GET":
		# return image
		return HttpResponse(status=status.HTTP_404_NOT_FOUND)
	elif request.method == "POST":
		form = PredefinedServiceForm()

		# get and save image
		form = PredefinedServiceForm(request.POST, request.FILES)

		if form.is_valid():

			print form.cleaned_data

			title = form.cleaned_data['title']
			description = form.cleaned_data['description']
			image = form.cleaned_data['image']
			print image

			new_object = PredefinedService(title=title, description=description, image=image)
			new_object.save()

			return HttpResponse(status=status.HTTP_201_CREATED)
		else:
			print form.errors
			print form.cleaned_data
			return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	return HttpResponseRedirect('/')








