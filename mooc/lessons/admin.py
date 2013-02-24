from django.contrib import admin
from lessons.models import (Achievement, World, Stage,
                            QuizChallenge, QuizQuestion)


admin.site.register(Achievement)
admin.site.register(World)
admin.site.register(Stage)

admin.site.register(QuizChallenge)
admin.site.register(QuizQuestion)

