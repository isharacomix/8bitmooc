# -*- coding: utf-8 -*-
from django.contrib import admin
from projects.models import Project, ProjectCommit

admin.site.register(Project)
admin.site.register(ProjectCommit)

