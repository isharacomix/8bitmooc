# -*- coding: utf-8 -*-
from django.contrib import admin
from world.models import (Achievement, World, Stage,
                          QuizChallenge, QuizQuestion, ChallengeSOS)


admin.site.register(Achievement)
admin.site.register(World)
admin.site.register(Stage)

admin.site.register(QuizChallenge)
admin.site.register(QuizQuestion)

admin.site.register(ChallengeSOS)

