# -*- coding: utf-8 -*-
# Define the app name to be used in the urls.py
# in this way, you do not need to type the app name in the beginning of each url
# Also, you can avoid the overlap between urls which contains common sub-address of urls

from __future__ import unicode_literals

from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    name = 'analytics'
