# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from lensapp.models import UserProfile, Photo

admin.site.register(UserProfile)
admin.site.register(Photo)