"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.conf.urls import url, include
	2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from app import views 

urlpatterns = [
	url(r'^admin/', admin.site.urls),

	# GET:		Loads offered services along with all it's images.
	# POST:		Posts an offered service.
	# PUT:		Updates an existing offered service.
	# DELETE:	Deletes offered service and it's images.
	url(r'^offeredservice/$', views.OfferedServiceView.as_view()),
	url(r'^offeredservice/(?P<pk>[0-9]+)/', views.OfferedServiceView.as_view()),

	# GET:	Loads public services (with/without) their bids.
	# POST:	Posts a public service.
	# PUT:	Updates an existing public service.
	url(r'^publicservice/$', views.PublicServiceView.as_view()),
	url(r'^publicservice/(?P<pk>[0-9]+)/', views.PublicServiceView.as_view()),

	# GET:	Loads all bids from a public service.
	# POST:	Posts a bid on a public service.
	# PUT:	Update existing bid.
	url(r'^bid/(?P<pk>[0-9]+)/', views.BidView.as_view()),

	# Unnecessary now, will be used later when saving actual image files
	## only if it's more efficient to not load images in the offered
	## list view, and only load them in the detail view
	# GET:		Loads images of an offered service.
	# POST:		Posts an images on an offered service.
	# DELETE:	Deletes an image from an offered service.
	url(r'^offeredimages/(?P<pk>[0-9]+)/', views.ServiceImagesView.as_view()),

	url(r'^profile/$', views.ProfileView.as_view()),
	
	url(r'^signup/$', views.signup),
	url(r'^logout/$', views.logout_view),
	url(r'^login/', views.token_request),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
