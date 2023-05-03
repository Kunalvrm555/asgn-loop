from django.contrib import admin

# Register your models here.

from .models import Store, StoreStatus, BusinessHours

admin.site.register(Store)
admin.site.register(StoreStatus)
admin.site.register(BusinessHours)
