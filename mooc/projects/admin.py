# -*- coding: utf-8 -*-
from django.contrib import admin
from projects.models import Project, ProjectCommit, ProjectComment

admin.site.register(Project)
admin.site.register(ProjectCommit)
admin.site.register(ProjectComment)

