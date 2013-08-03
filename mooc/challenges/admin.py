# -*- coding: utf-8 -*-
from django.contrib import admin
from challenges.models import Challenge, SOS, Feedback

admin.site.register(Challenge)
admin.site.register(SOS)
admin.site.register(Feedback)

