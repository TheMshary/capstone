from django.contrib import admin
from app.models import PredefinedService, ServiceImage

# Register your models here.
admin.site.register(PredefinedService)
admin.site.register(ServiceImage)