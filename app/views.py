#============================= CORE IMPORTS =============================#
import pprint
import time
from copy import deepcopy

#============================ DJANGO IMPORTS ============================#
from django.template import RequestContext
from django.db import IntegrityError
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User, AnonymousUser
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
	PublicServiceProviderBidSerializer,
	PublicServiceSerializer, 
	ProfileSerializer,
)

# Create your views here.


class SearchView(APIView):
	"""
	View for searching Providers based on rating and/or category
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request):
		category = request.data.get('category')
		profiles = Profile.objects.filter(category=category).order_by('rating__rate')
		serializer = ProfileSerializer(profiles, many=True)

		return Response(serializer.data, status=status.HTTP_200_OK)


class ProviderWorkingOnView(APIView):
	"""
	View for getting active services of the logged in Provider
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		services = Service.objects.filter(status='active', providerpk=request.user.pk)

		special = services.filter(is_special=True)
		offeredservices = services.exclude(offeredservice=None)

		offered = []
		for serv in offeredservices:
			offered.append(serv.offeredservice)

		publicservices = services.filter(offeredservice=None, is_special=False)

		public = []
		for serv in publicservices:
			public.append(serv.publicservice)
			

		offeredserializer = OfferedServiceSerializer(offered, many=True)
		specialserializer = ServiceSerializer(special, many=True)
		publicserializer = PublicServiceSerializer(public, many=True)

		data = {
			'special': specialserializer.data,
			'offered': offeredserializer.data,
			'public': publicserializer.data
		}
		return Response(data, status=status.HTTP_200_OK)


class ProviderRequestsView(APIView):
	"""
	View for getting requested services of the logged in Provider
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		services = Service.objects.filter(status='pending', providerpk=request.user.pk)

		special = services.filter(is_special=True)
		offeredservices = services.exclude(offeredservice=None)

		offered = []
		for serv in offeredservices:
			offered.append(serv.offeredservice)

		offeredserializer = OfferedServiceSerializer(offered, many=True)
		specialserializer = ServiceSerializer(special, many=True)

		data = {
			'special': specialserializer.data,
			'offered': offeredserializer.data,
		}
		return Response(data, status=status.HTTP_200_OK)


class AcceptBidView(APIView):
	"""
	Seeker accepting a bid
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request):
		pk = request.data.get('pk')
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

		# update service's price and status and providerpk
		service.service.price = bid.bid
		service.service.providerpk = bid.bidder.pk
		service.service.status = "active"
		service.service.save()
		service.save()

		return Response(status=status.HTTP_200_OK)


class DeclineBidView(APIView):
	"""
	Seeker declining a bid
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request):
		pk = request.data.get('pk')
		bid = Bid.objects.get(pk=pk)

		bid.status = "declined"
		bid.save()

		return Response(status=status.HTTP_200_OK)


class ProviderDoneView(APIView):
	"""
	Provider "Dones" the service they're working on
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request):
		pk = request.data.get('pk')
		service = self._get_service(pk)
		service.status = "done"
		service.save()

		return Response(status=status.HTTP_200_OK)

	def _get_service(self, pk):
		try:
			return Service.objects.get(pk=pk)
		except Service.DoesNotExist, e:
			raise Http404


class ProviderResponseView(APIView):
	"""
	Provider can accept or decline a request for an Offered Service
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request):
		pk = request.data.get('pk')
		service = self._get_service(pk)
		response = request.data.get("response")

		if response == "accept":
			service.status = "active"
		elif response == "decline":	
			service.status = "declined"
		else:
			return Response({"msg": "'response' can be either 'accept' or 'decline', spelled exactly that way."},
							status=status.HTTP_400_BAD_REQUEST)

		service.save()

		return Response(status=status.HTTP_200_OK)

	def _get_service(self, pk):
		try:
			return Service.objects.get(pk=pk)
		except Service.DoesNotExist, e:
			raise Http404


class RequestView(APIView):
	"""
	View for requesting services
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request):
		pk = request.data.get('servicepk')
		try:
			offered = OfferedService.objects.get(pk=pk)
		except OfferedService.DoesNotExist, e:
			return Response(status=status.HTTP_404_NOT_FOUND)

		# duplicate the base service object and change status to 'pending'
		service = offered.service
		service = deepcopy(service)
		service.pk = None
		service.status = "pending"
		service.seekerpk = request.user.pk
		service.save()

		# duplicate offered service object
		newoffered = deepcopy(offered)
		newoffered.service = None
		newoffered.pk = None
		newoffered.save()
		newoffered.service = service
		newoffered.save()




		# the force_insert=True forces .save() to create a new instance (force SQL insert).
		# serv = Service.objects.create()
		# service.service.pk = serv.pk
		# serv2 = OfferedService.objects.create()
		# # return Response("service: %s ---- serv2: %s" % (service.pk, serv2.pk))
		# service.pk = serv2.pk

		# serv.delete()
		# serv2.delete()
		# service.service.status = "pending"
		# service.service.seekerpk = request.user.pk
		# service.service.save(force_insert=True) # This is commented because it doesn't update the pk, and idk how to do that
		# service.save(force_insert=True)

		##### BAD CODE
		# serv = OfferedService.objects.create()
		# baseservice = Service.objects.create()

		# serv.service = baseservice
		# serv.category = service.category
		
		# serv.service.title = service.service.title
		# serv.service.description = service.service.description
		# serv.service.price = service.service.price
		# serv.service.status = "pending"
		# serv.service.due_date = service.service.due_date
		# serv.service.created = service.service.created
		# serv.service.seekerpk = request.user.pk
		# serv.service.providerpk = service.service.providerpk
		# serv.service.is_special = service.service.is_special

		# for image in ServiceImage.objects.filter(service=service):
		# 	ServiceImage.objects.create(service=serv, image=image, created=image.created)

		# serv.service.save()
		# serv.save()
		##### /BAD CODE


		serializer = OfferedServiceSerializer(newoffered)
		# serializer2 = OfferedServiceSerializer(data=serializer.data)
		# if serializer2.is_valid():
		# 	serializer2.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProfileView(APIView):
	"""
	Provider Profile retrieval and updating.
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		pk = request.GET.get('pk', None)
		if pk is None:
			profile = request.user.profile
		else:
			profile = self._get_profile(pk)
		serializer = ProfileSerializer(profile)
		return Response(serializer.data, status=status.HTTP_200_OK)

	def put(self, request):
		profile = request.user.profile
		data = request.data

		serializer = ProfileSerializer(profile, data=data, context={"category":data.get("category")})
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def _get_profile(self, pk):
		try:
			return Profile.objects.get(user__pk=pk)
		except Profile.DoesNotExist, e:
			raise Http404

class OfferedServiceView(APIView):
	"""
	Offered Service listing (ordered by date created), creation, updating, and deletion.
	"""

	authentication_classes = (TokenAuthentication,)
	# permission_classes = (IsAuthenticated,)

	@permission_classes((AllowAny,))
	def get(self, request):
		query_last = request.GET.get('query_last', None)
		servicepk = request.GET.get('servicepk', None)
		if servicepk is None:
			services = OfferedService.objects.filter(service__status="available").order_by('-service__created')[:query_last]

			serializer = OfferedServiceSerializer(services, many=True)
			return Response(serializer.data, status=status.HTTP_200_OK)

		else:
			service = self._get_object(servicepk)
			serializer = OfferedServiceSerializer(service)
			return Response(serializer.data, status=status.HTTP_200_OK)

	@permission_classes((IsAuthenticated,))
	def post(self, request):
		providerpk = request.user.pk
		data = request.data
		data.get('service').update({"providerpk":providerpk, 'status':'available'})
		serializer = OfferedServiceSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@permission_classes((IsAuthenticated,))
	def put(self, request):
		pk = request.data.get('servicepk', None)
		service = self._get_object(pk)
		serializer = OfferedServiceSerializer(service, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@permission_classes((IsAuthenticated,))
	def delete(self, request):
		pk = request.data.get('servicepk', None)
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


class OfferedServiceOfProviderView(APIView):
	"""
	Offered Service listing (ordered by date created), from a certain Provider.
	"""

	# authentication_classes = (TokenAuthentication,)
	# permission_classes = (IsAuthenticated,)

	@permission_classes((AllowAny,))
	def get(self, request):
		providerpk = request.GET.get('providerpk', None)
		if providerpk is None:
			raise Http404

		services = OfferedService.objects.filter(service__providerpk=providerpk, service__status='available')
		services = services.order_by('-service__created')

		serializer = OfferedServiceSerializer(services, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

class pubsView(APIView):
	permission_classes = (AllowAny,)

	def get(self, request):
		query_last = request.GET.get('query_last', None) # parameters + JSON encoding = 500
		servicepk = request.GET.get('servicepk', None)
		if servicepk is None:
			services = PublicService.objects.all().order_by('-service__created')[:query_last]
			serializer = PublicServiceSerializer(services, many=True)
			data = {'feed':serializer.data}

			user = request.user
			if user.is_anonymous():		# This is not working (based on the error logs), figure this out.
				bidon = Bid.objects.filter(bidder=user)
				services = []
				for bid in bidon:
					services.append(bid.service)

				serviceserializer = PublicServiceProviderBidSerializer(bidon, many=True)

				data.update({'bids':serviceserializer.data})
			return Response(data, status=status.HTTP_200_OK)
		else:
			service = self._get_object(servicepk)
			serializer = PublicServiceSerializer(service)
			return Response(serializer.data, status=status.HTTP_200_OK)

	def _get_object(self, pk):
		try:
			return PublicService.objects.get(pk=pk)
		except PublicService.DoesNotExist, e:
			raise Http404


class SpecialServiceView(APIView):
	"""
	Public Service listing (ordered by date created), creation, updating, and deletion.
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	# @permission_classes((AllowAny,))
	def get(self, request):
		pk = request.GET.get('pk', None)
		service = self._get_object(pk)
		serializer = SpecialServiceSerializer(service)
		return Response(serializer.data, status=status.HTTP_200_OK)

	def _get_object(self, pk):
		try:
			return Service.objects.get(pk=pk)
		except Service.DoesNotExist, e:
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
		servicepk = request.GET.get('servicepk', None)
		if servicepk is None:
			services = PublicService.objects.filter(service__status="pending").order_by('-service__created')[:query_last]

			user = request.user
			if user is not AnonymousUser:
				bidon = Bid.objects.filter(bidder=user, publicservice__service__status="pending")
				serviceserializer = PublicServiceProviderBidSerializer(bidon, many=True)

				services = services.exclude(bid__in=Bid.objects.filter(bidder=user))
				serializer = PublicServiceSerializer(services, many=True)

				data = {'feed':serializer.data}
				data.update({'bids':serviceserializer.data})
			else:
				serializer = PublicServiceSerializer(services, many=True)
				data = {'feed':serializer.data}
			return Response(data, status=status.HTTP_200_OK)
		else:
			service = self._get_object(servicepk)
			serializer = PublicServiceSerializer(service)
			return Response(serializer.data, status=status.HTTP_200_OK)

	@permission_classes((IsAuthenticated,))
	def post(self, request):
		# Do an if-statement to check if the service is suppose to be special.
		# If it is, do the code block for a special service, may need a dedicated serializer for special services
		# If not, then do the code block for a public service, it's already written below...
		seekerpk = request.user.pk
		data = request.data
		data.get('service').update({"seekerpk": seekerpk})
		serializer = PublicServiceSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@permission_classes((IsAuthenticated,))
	def put(self, request):
		pk = request.data.get('pk')
		service = self._get_object(pk)
		serializer = PublicServiceSerializer(service, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@permission_classes((IsAuthenticated,))
	def delete(self, request):
		pk = request.data.get('pk')
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


class SpecialServiceView(APIView):
	"""
	Special Service listing (ordered by date created), creation, updating, and deletion.
	"""

	authentication_classes = (TokenAuthentication,)
	# permission_classes = (IsAuthenticated,)

	@permission_classes((IsAuthenticated,))
	def get(self, request):
		# query_last = request.GET.get('query_last', None)
		servicepk = request.GET.get('servicepk', None)
		# if servicepk is None:
		# 	services = SpecialService.objects.all().order_by('-service__created')[:query_last]

		# 	serializer = SpecialServiceSerializer(services, many=True)
		# 	data = {'services':serializer.data}
		# else:
		service = self._get_object(servicepk)
		serializer = SpecialServiceSerializer(service)
		return Response(serializer.data, status=status.HTTP_200_OK)
		

	@permission_classes((IsAuthenticated,))
	def post(self, request):
		seekerpk = request.user.pk
		data = request.data
		providerpk = data.pop('providerpk')
		stuffington_post = {
			'seekerpk': seekerpk,
			'providerpk': providerpk,
			'is_special': True
		}
		serializer = SpecialServiceSerializer(data=data, context={"service": stuffington_post})
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@permission_classes((IsAuthenticated,))
	def put(self, request):
		pk = request.data.get('pk')
		service = self._get_object(pk)
		serializer = SpecialServiceSerializer(service, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@permission_classes((IsAuthenticated,))
	def delete(self, request):
		pk = request.data.get('pk')
		service = self._get_object(pk)
		service.delete()
		return Response(status=status.HTTP_200_OK)

	def _get_object(self, pk):
		try:
			return Service.objects.get(pk=pk)
		except Service.DoesNotExist, e:
			raise Http404


class BidView(APIView):
	"""
	Bid retrieval based on Public Service, creation, updating, and deletion.
	"""

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		pk = request.GET.get('pk')
		query_last = request.GET.get('query_last', None)
		try:
			service = PublicService.objects.get(pk=pk)
		except PublicService.DoesNotExist, e:
			raise Http404
		bids = Bid.objects.filter(service=service)[:query_last]
		serializer = BidSerializer(bids, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

	def post(self, request):
		data = request.data
		# data.update({'bidder':request.user})
		serializer = BidSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request):
		data = request.data
		pk = data.pop('pk')
		bid = self._get_object(pk)
		serializer = BidSerializer(bid, data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request):
		pk = request.data.get('pk')
		bid = self._get_object(pk)
		bid.delete()
		return Response(status=status.HTTP_200_OK)

	def _get_object(self, pk):
		try:
			return Bid.objects.get(pk=pk)
		except Bid.DoesNotExist, e:
			raise Http404


class ServiceImagesView(APIView):
	"""
	Offered Service Images listing, creation, and deletion.
	"""

	authentication_classes = (TokenAuthentication,)
	# permission_classes = (IsAuthenticated,)

	@permission_classes((AllowAny,))
	def get(self, request):
		pk = request.data.get('pk')
		service = self._get_service(pk)
		query_last = request.GET.get('query_last', None)
		images = ServiceImage.objects.filter(service=service)[:query_last]
		serializer = ServiceImageSerializer(images, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@permission_classes((IsAuthenticated,))
	def post(self, request):
		pk = request.data.get('pk')
		service = self._get_service(pk)
		data = request.data
		serializer = ServiceImageSerializer(data=data, context={"service":service})
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@permission_classes((IsAuthenticated,))
	def delete(self, request):
		pk = request.data.get('pk')
		image = self._get_image(pk)
		image.delete()
		return Response(status=status.HTTP_200_OK)

	def _get_image(self, pk):
		try:
			return ServiceImage.objects.get(pk=pk)
		except ServiceImage.DoesNotExist, e:
			return Response(status=status.HTTP_404_NOT_FOUND)

	def _get_service(self, pk):
		try:
			return OfferedService.objects.get(pk=pk)
		except OfferedService.DoesNotExist, e:
			return Response(status=status.HTTP_404_NOT_FOUND)

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
		services = []
		if usertype == "seeker":
			try:
				services = Service.objects.filter(seekerpk=user.pk)[:query_last]
			except Service.DoesNotExist, e:
				return Response({"msg":"SORRY"}, status=status.HTTP_400_BAD_REQUEST)
		elif usertype == "provider":
			try:
				services = Service.objects.filter(providerpk=user.pk)[:query_last]
			except Service.DoesNotExist, e:
				return Response({"msg":"sorry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({"msg": "'usertype' is neither seeker nor provider."}, status=status.HTTP_400_BAD_REQUEST)
		
		serializer = ServiceLogSerializer(services, many=True)
		# return Response("gibbirish", status=status.HTTP_200_OK)
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
		return Response(status=status.HTTP_404_NOT_FOUND)
	

	token_string = "Token %s" % token
	usertype = user.profile.usertype
	data = {
		"token": token_string,
		"usertype": usertype,
		"pk": user.pk
	}
	return Response(data, status=status.HTTP_200_OK)

@api_view(["POST"])
@csrf_exempt
@permission_classes((AllowAny,))
def signup(request):
	try:
		User.objects.get(username=request.data.get("username"))
		return Response({'msg':"Username taken."}, status=status.HTTP_400_BAD_REQUEST)
	except User.DoesNotExist:
		pass

	usertype = request.data.get("usertype")

	serializer = UserSerializer(data=request.data)
	if serializer.is_valid():
		user_instance = serializer.save()
		if usertype != 'seeker' and usertype != 'provider':
			return Response({'msg':'Invalid usertype.'}, status=status.HTTP_400_BAD_REQUEST)
		user_instance.profile.usertype = usertype
		user_instance.profile.save()

		return Response(serializer.data, status=status.HTTP_201_CREATED)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@csrf_exempt
def logout_view(request):
	logout(request)
	return Response({'msg':"LOGGED OUT"}, status=status.HTTP_204_NO_CONTENT)


