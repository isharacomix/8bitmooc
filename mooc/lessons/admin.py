from django.contrib import admin
from lessons.models import Milestone, Module, Lesson, DummyChallenge

admin.site.register(Milestone)
admin.site.register(Module)
admin.site.register(Lesson)

admin.site.register(DummyChallenge)

