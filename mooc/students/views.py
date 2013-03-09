# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from world.models import Stage, World
from students.models import Student
from django.contrib.auth.models import User

import random


# Display a student's profile page.
def view_profile(request, username):
    try:
        student = Student.objects.get( user=User.objects.get(username=username) )
    except exceptions.ObjectDoesNotExist: raise Http404()

    return render( request, 'students_profile.html', {'student': student} )


# This logs a user in, provided the password and stuff is right. :P
def login_page(request):
    if request.user.is_authenticated():
        return redirect("dashboard")
    elif request.method == 'POST':
        if request.POST.get("register") == "register": return redirect("register")
        if request.POST.get("login") == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.student:
                    login(request, user)
                    return redirect("dashboard")
                else:
                    return render(request, 'login.html',
                                       {'alerts': [{"tags":"alert-error",
                                                    "content":"This account has not yet been activated." }]} )
            else:
                return render(request, 'login.html',
                                       {'alerts': [{"tags":"alert-error",
                                                    "content":"Incorrect username or password." }]} )
    else:
        return render(request, 'login.html')


# This is the register page. If we have a POST request, we DO the register.
def register_page(request):
    if request.user.is_authenticated():
        return redirect("dashboard")
    elif request.method == 'POST':
        return do_register(request)
    else:
        return render(request, 'login.html')
    

# This is the register page. If we have a POST request, we DO the register.
def logout_page(request):
    if request.user.is_authenticated():
        logout(request)
        return render( request, "logout.html", {"alerts":[{"tags":"alert-success",
                                                          "content":"You have successfully logged out."}]} )
    else:
        return redirect("login")
    


