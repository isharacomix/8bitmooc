# -*- coding: utf-8 -*-
from django.contrib import admin
from students.models import Student, LogEntry

admin.site.register(Student)
admin.site.register(LogEntry)

