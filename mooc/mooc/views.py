# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.models import User

from students.models import Student, LogEntry


# This views the home page. If the user is logged in, we redirect to the
# dashboard. This is non-dynamic.
def view_index(request):
    me = Student.from_request(request)
    
    if me and not me.agreed: return redirect("terms")
    elif me and me.banned: return redirect("logout")
    elif me: return view_dashboard(request, me)
    
    return render(request,
                  "index.html",
                  {'alerts': request.session.pop('alerts', []) })
    

# This is the dashboard for the student (or TA!). This displays the news and
# announcements on the left side of the page, the remaining challenges on the
# right, and all of the buttons to other locations in the site.
def view_dashboard(request, me):
    return render(request,
                  "dashboard.html",
                  {'alerts': request.session.pop('alerts', []) })


# View the embedded IRC!
@Student.permission
def webchat(request):
    me = Student.from_request(request)
    LogEntry.log(request, "chat")
    return render(request, "chat.html")

