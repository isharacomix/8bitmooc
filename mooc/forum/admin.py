# -*- coding: utf-8 -*-
from django.contrib import admin
from forum.models import DiscussionBoard, DiscussionTopic, DiscussionPost

admin.site.register(DiscussionBoard)
admin.site.register(DiscussionTopic)
admin.site.register(DiscussionPost)

