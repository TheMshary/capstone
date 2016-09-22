#============================= CORE IMPORTS =============================#
import pprint

#============================ DJANGO IMPORTS ============================#
from django.template import RequestContext
from django.db import IntegrityError
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt

#======================== REST FRAMEWORK IMPORTS ========================#
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authtoken.models import Token
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
	ServiceLogSerializer,
	BidSerializer,
	OfferedServiceSerializer, 
	PublicServiceSerializer, 
	ProfileSerializer, 
)

# Create your views here.


##############################
########## UNTESTED ##########
######## UNREFACTORED ########
##############################
class AcceptBidView(APIView):
	"""
	Seeker accepting a bid
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, pk):
		bid = Bid.objects.get(pk=pk)

		service = bid.service
		otherbids = service.bid_set.all()

		# decline all other bids
		for otherbid in otherbids:
			otherbid.status = "declined"
			otherbid.save()
		
		# accept this bid
		bid.status = "accepted"
		bid.save()

		# update service's price and status
		service.price = bid.bid
		service.status = "active"
		service.save()


		return Response(status=status.HTTP_200_OK)


##############################
########## UNTESTED ##########
######## UNREFACTORED ########
##############################
class DeclineBidView(APIView):
	"""
	Seeker declining a bid
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, pk):
		bid = Bid.objects.get(pk=pk)

		bid.status = "declined"
		bid.save()

		return Response(status=status.HTTP_200_OK)

##############################
########## UNTESTED ##########
######## UNREFACTORED ########
##############################
class ProviderDoneView(APIView):
	"""
	Provider "Dones" the service they're working on
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, pk):
		service = Service.objects.get(pk=pk)
		service.status = "Done"
		service.save()

		return Response(status=status.HTTP_201_CREATED)

##############################
########## UNTESTED ##########
######## UNREFACTORED ########
##############################
class ProviderResponseView(APIView):
	"""
	Provider can accept or decline a request for an Offered Service
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, pk):
		service = Service.objects.get(pk=pk)
		response = request.data.get("response")

		if response == "accept":
			service.status = "Active"
		elif response == "decline":	
			service.status = "Declined"
		else:
			return Response({"msg": "Correct your spelling Ali!"}, status=status.HTTP_400_BAD_REQUEST)

		service.save()

		return Response(status=status.HTTP_201_CREATED)

##############################
########## UNTESTED ##########
######## UNREFACTORED ########
##############################
class RequestView(APIView):
	"""
	View for requesting services
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, pk):
		service = Service.objects.get(pk=pk)

		service.seekerpk = request.user.pk
		service.status = "pending"

		# the force_insert=True forces .save() to create a new instance (force SQL insert).
		service.save(force_insert=True)

		return Response(status=status.HTTP_201_CREATED)


class ProfileView(APIView):
	"""
	Provider Profile retrieval and updating.
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		user = request.user
		profile = user.profile
		serializer = ProfileSerializer(profile)
		return Response(serializer.data, status=status.HTTP_200_OK)

	def put(self, request):
		profile = request.user.profile
		data = request.data
		serializer = ProfileSerializer(profile, data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfferedServiceView(APIView):
	"""
	Offered Service listing (ordered by date created), creation, updating, and deletion.
	"""

	authentication_classes = (TokenAuthentication,)
	# permission_classes = (IsAuthenticated,)

	@permission_classes((AllowAny,))
	def get(self, request):
		query_last = request.GET.get('query_last', None)
		services = OfferedService.objects.all()[:query_last].order_by(created)
		serializer = OfferedServiceSerializer(services, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)


	@permission_classes((IsAuthenticated,))
	def post(self, request):
		providerpk = request.user.pk
		data = request.data
		serializer = OfferedServiceSerializer(data=data, context={"service":{"providerpk":providerpk}})
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
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
	Public Service listing (ordered by date created), creation, updating, and deletion.
	"""

	authentication_classes = (TokenAuthentication,)
	# permission_classes = (IsAuthenticated,)

	@permission_classes((AllowAny,))
	def get(self, request):
		query_last = request.GET.get('query_last', None)
		services = PublicService.objects.all()[:query_last].order_by(created)
		serializer = PublicServiceSerializer(services, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@permission_classes((IsAuthenticated,))
	def post(self, request):
		seekerpk = request.user.pk
		data = request.data
		serializer = PublicServiceSerializer(data=data, context={"service": {"seekerpk":seekerpk}})
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
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
	Bid retrieval based on Public Service, creation, updating, and deletion.
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, pk):
		query_last = request.GET.get('query_last', None)
		service = PublicService.objects.get(pk=pk)
		bid = Bid.objects.all(service=service)[:query_last]
		serializer = BidSerializer(services, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

	def post(self, request, pk):
		data = request.data
		serializer = BidSerializer(data=data, context={"service":pk})
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, pk):
		bid = self._get_object(pk)
		serializer = BidSerializer(bid, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

	def delete(self, request, pk):
		bid = self._get_object(pk)
		bid.delete()
		return Response(status=status.HTTP_200_OK)

	def _get_object(self, pk):
		try:
			return Bid.objects.get(pk=pk)
		except PublicService.DoesNotExist, e:
			raise Http404


class ServiceImagesView(APIView):
	"""
	Offered Service Images listing, creation, and deletion.
	"""

	authentication_classes = (TokenAuthentication,)
	# permission_classes = (IsAuthenticated,)

	@permission_classes((AllowAny,))
	def get(self, request, pk):
		service = self._get_service_object(pk)
		images = ServiceImage.objects.all(service=service)
		serializer = ServiceImageSerializer(images, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@permission_classes((IsAuthenticated,))
	def post(self, request, pk):
		service = self._get_service_object(pk)
		data = request.data
		serializer = ServiceImageSerializer(data=data, context={"service":service})
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@permission_classes((IsAuthenticated,))
	def delete(self, request, pk):
		image = self._get_image_object(pk)
		image.delete()
		return Response(status=status.HTTP_200_OK)

	def _get_image_object(self, pk):
		try:
			return ServiceImage.objects.get(pk=pk)
		except ServiceImage.DoesNotExist, e:
			raise Http404

	def _get_service_object(self, pk):
		try:
			return OfferedService.objects.get(pk=pk)
		except OfferedService.DoesNotExist, e:
			raise Http404

##############################
########## UNTESTED ##########
##############################
class LogView(APIView):
	"""
	Service Log listing of the logged in user.
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		user = request.user
		query_last = request.GET.get('query_last', None)
		usertype = user.profile.usertype
		if usertype == "seeker":
			services = Service.objects.filter(seekerpk=user.pk)[:query_last]
		elif usertype == "provider":
			services = Service.objects.filter(providerpk=user.pk)[:query_last]
		else:
			return Response({"msg": "'usertype' is neither seeker nor provider."}, status=status.HTTP_400_BAD_REQUEST)
		
		serializer = ServiceLogSerializer(services, many=True)
		# serializer = ServiceSerializer(services, many=True)

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
	except Token.DoesNotExist, e:
		raise Http404
	

	token_string = "Token %s" % token
	usertype = user.profile.usertype
	data = {
		"token": token_string,
		"usertype": usertype
	}
	return Response(data, status=status.HTTP_200_OK)

@api_view(["POST"])
@csrf_exempt
@permission_classes((AllowAny,))
def signup(request):
	try:
		User.objects.get(username=request.data.get("username"))
		return HttpResponse("Username taken.", status=status.HTTP_400_BAD_REQUEST)
	except User.DoesNotExist:
		pass

	usertype = request.data.get("usertype")

	serializer = UserSerializer(data=request.data)
	if serializer.is_valid():
		user_instance = serializer.save()
		user_instance.profile.usertype = usertype
		user_instance.save()
		
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	return HttpResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@csrf_exempt
def logout_view(request):
	logout(request)
	return HttpResponse("LOGGED OUT", status=status.HTTP_204_NO_CONTENT)


