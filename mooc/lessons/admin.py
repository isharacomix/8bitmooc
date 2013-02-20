from django.contrib import admin
from lessons.models import (Milestone, Module, Lesson,
                            QuizChallenge, QuizQuestion)


admin.site.register(Milestone)
admin.site.register(Module)
admin.site.register(Lesson)

admin.site.register(QuizChallenge)
admin.site.register(QuizQuestion)

