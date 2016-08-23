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
# from rest_framework.authtoken import views as token_views
from app import views 

urlpatterns = [
	url(r'^admin/', admin.site.urls),

	url(r'^predefinedservice/$', views.PredefinedServiceList.as_view()),
	url(r'^predefinedservice/(?P<pk>[0-9]+)/$', views.PredefinedServiceDetail.as_view()),


    # url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^admin/', include(admin.site.urls)),

	# url(r'^', include('django.contrib.auth.urls')),
	# url(r'^accounts/', include('allauth.urls')),

	# url(r'^rest-auth/', include('rest_auth.urls')),
	# url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),

	# url(r'^api-token-auth/', token_views.obtain_auth_token),
	
	url(r'^signup/$', views.signup),
	# url(r'^login/$', views.login_view),
	url(r'^logout/$', views.logout_view),

	url(r'^$', views.test),
	url(r'^test_delete/', views.test_delete),
	url(r'^api_test/', views.api_test),
	url(r'^api_test_json/', views.api_test_json),

	# url(r'^predefinedservice/$', views.predefinedservice),
	url(r'^test_image/$', views.image_test),


	url(r'^login/', views.TokenRequest.as_view()),
	url(r'^token/', views.token_request),
	url(r'^test', views.test),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
