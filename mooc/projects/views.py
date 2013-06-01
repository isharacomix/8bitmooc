# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from students.models import Student, LogEntry
from projects.models import Project
from django.contrib.auth.models import User

import random


# The user can filter out projects based on whether they work on them, the
# project needs help, or they have favorited it.
def project_list(request):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if not me:
        request.session["alerts"].append(("alert-error","Please sign in first."))
        return redirect("sign-in")   
    
    # Retrieve GET parameters.
    filt = request.GET.get("filter")
    page = request.GET.get("page")
    if page and page.isdigit(): page = max(0, int(page)-1)
    else: page = 0
    pagination = 50
    
    # Filter the project list based on the GET filter parameter.
    project_list = []
    if filt == "help":
        project_list += list(Project.objects.filter(is_public=True, help_wanted=True))
    elif filt == "watch":
        project_list += list(me.watches.filter(is_public=True))
    elif filt == "all":
        project_list += list(me.owns.filter(is_public=False))
        project_list += list(me.works_on.filter(is_public=False))
        project_list += list(Project.objects.filter(is_public=True))
    else:
        project_list += list(me.owns.all())
        project_list += list(me.works_on.all())
        filt = "mine"
    project_list = project_list[page*pagination:(page+1)*pagination]
    
    # TODO: Create the spotlight.
    
    
    return render( request, "project_list.html", {'projects':project_list,
                                                  'alerts': request.session.pop('alerts', []),
                                                  'page': page+1,
                                                  'pages': (len(project_list)/pagination)+1,
                                                  'filter': filt } )


# This is the screen where students can edit projects and see each others' code.
def view_project(request, id):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if not me:
        request.session["alerts"].append(("alert-error","Please sign in first."))
        return redirect("sign-in")   
    raise Http404()
    
