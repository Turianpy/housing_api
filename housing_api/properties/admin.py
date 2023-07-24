from django.contrib import admin

from .models import Image, Location, Property, RentDetails

admin.site.register([Property, Image, Location, RentDetails])
