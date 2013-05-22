# -*- coding: utf-8 -*-
from django.contrib import admin
from challenges.models import Challenge, ChallengeResponse

admin.site.register(Challenge)
admin.site.register(ChallengeResponse)

