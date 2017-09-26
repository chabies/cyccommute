# -*- coding: utf-8 -*-
# This sets admin for tables of the database
from __future__ import unicode_literals

from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin # use leaflet
from .models import GPXPoint


# Register your models here.

class GPXPointAdmin(LeafletGeoAdmin):
    list_display = ('gpxfile','timestamp')




admin.site.register(GPXPoint)
