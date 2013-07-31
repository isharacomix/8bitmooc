# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.utils import timezone 

import hashlib
import urllib2
import json

from django.contrib.auth.models import User

from students.models import Student, LogEntry


# This redirects and starts the github handshake.
def handle_login(request):
    me = Student.from_request(request)
    
    if me:
        request.session["alerts"].append(("alert-error","You are already logged in!"))
        return redirect("index")
    
    return redirect("https://github.com/login/oauth/authorize?client_id=%s&scope=user:email"%settings.GITHUB_ID)


# When a user logs into Github, this is the function that will be called
# so that we can handle the login procedure.
def handle_oauth(request):
    me = Student.from_request(request)
    
    # Github will give us a code. If we don't get the code, fail early.
    if "code" not in request.GET:
        request.session["alerts"].append(("alert-error","Error getting token from Github."))
        return redirect("index")    
    
    # Send the data to Github and get our token!
    keys = (settings.GITHUB_ID, settings.GITHUB_SECRET, request.GET["code"])
    response = urllib2.urlopen('https://github.com/login/oauth/access_token',
                               'client_id=%s&client_secret=%s&code=%s'%keys)
    data = response.read()
    if "access_token" not in data:
        request.session["alerts"].append(("alert-error","Error getting token from Github."))
        return redirect("index")    
    
    # Get the token.
    token = data[data.find("=")+1:data.find("&")]
    request.session["access_token"] = token
    
    # Now, we find out the user's name and e-mail address. If this user has an
    # account, we log them in. If not, we create an account for them.
    response = urllib2.urlopen('https://api.github.com/user/?access_token=%s'%token)
    apidata = json.loads(response.read())
    
    # Get the user and username. If the user is in the db, log it in. Otherwise,
    # create an account.
    username = apidata["login"]
    email = apidata["email"]
    try: user = User.objects.get(username=username)
    except exceptions.ObjectDoesNotExist: user = None
    
    # Log in or create the account.
    if user:
        login(request, user)
        request.session["alerts"].append(("alert-success","Welcome back, %s!"%username))
        return redirect("index")
    else:
        user = User.objects.create_user(username, email, str(random.randint(100000000,999999999)))
        user.save()
        student = Student(user=user)
        student.save()
        return redirect("index")
        
    
# This handles the logout process, clearing out the cookies and whatnot.
def handle_logout(request):
    me = Student.from_request(request)

    if me:
        logout(request)
        if "alerts" not in request.session: request.session["alerts"] = []
        request.session["alerts"].append(("alert-success","Successfully logged out - come back soon!"))
        return redirect("index") 
    else:
        request.session["alerts"].append(("alert-error","You're already logged out!"))
        return redirect("index") 


# If this is a post request, it means that the user has agreed to the terms of use
# and we can let them use the website.
def terms_of_use(request):
    me = Student.from_request(request)
    if not me:
        request.session["alerts"].append(("alert-error","Please log in to access this feature."))
        return redirect("index")
    
    # A POST request means that the user has agreed to the terms of use.
    if request.method == "POST":
        me.agreed = True
        me.save()
        request.session["alerts"].append(("alert-success","Thanks! Welcome to #8bitmooc!"))
        return redirect("index")
    
    # If they've already agreed, let them know.
    if me.agreed:
        request.session["alerts"].append(("alert-success","You have already agreed to the terms of use."))
    
    # Render the page.
    return render(request,
                  "terms_of_use.html",
                  {'alerts': request.session.pop('alerts', []) })

