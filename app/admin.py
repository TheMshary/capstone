from django.contrib import admin
from app.models import Profile, Service, PublicService, OfferedService, ServiceImage, Bid

# Register your models here.
admin.site.register(Profile)
admin.site.register(Service)
admin.site.register(PublicService)
admin.site.register(OfferedService)
admin.site.register(ServiceImage)
admin.site.register(Bid)