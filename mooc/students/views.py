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
import random

from django.contrib.auth.models import User

from students.models import Student, LogEntry
from nes.models import CodeSubmission
from challenges.models import Challenge


# This redirects and starts the github handshake.
def handle_login(request):
    me = Student.from_request(request)
    
    if me:
        request.session["alerts"].append(("alert-error","You are already logged in!"))
        return redirect("index")
    request.session["secret_state"] = str(random.randint(100000000,999999999))
    
    return redirect("https://github.com/login/oauth/authorize?client_id=%s&state=%s&scope=user:email"%
                    (settings.GITHUB_ID, request.session["secret_state"]))


# When a user logs into Github, this is the function that will be called
# so that we can handle the login procedure.
def handle_oauth(request):
    me = Student.from_request(request)
    
    # Github will give us a code. If we don't get the code or if the secrets
    # have been screwed up, fail early.
    if ("code" not in request.GET or request.session.get("secret_state") is None
       or request.GET.get("state") != request.session.get("secret_state")):
        request.session["alerts"].append(("alert-error","Error getting token from Github."))
        return redirect("index")    
    
    # Send the data to Github and get our token!
    keys = (settings.GITHUB_ID, settings.GITHUB_SECRET, request.GET["code"])
    try: response = urllib2.urlopen('https://github.com/login/oauth/access_token',
                                    'client_id=%s&client_secret=%s&code=%s'%keys)
    except:
        request.session["alerts"].append(("alert-error","Error getting token from Github."))
        return redirect("index") 
                               
    data = response.read()
    if "access_token" not in data:
        request.session["alerts"].append(("alert-error","Error getting token from Github."))
        return redirect("index")    
    
    # Get the token.
    token = data[data.find("=")+1:data.find("&")]
    request.session["access_token"] = token
    
    # Now, we find out the user's name and e-mail address. If this user has an
    # account, we log them in. If not, we create an account for them.
    try:
        response = urllib2.urlopen('https://api.github.com/user?access_token=%s'%token)
        userdata = json.loads(response.read())
        username = userdata["login"]
        try: user = User.objects.get(username=username)
        except exceptions.ObjectDoesNotExist:
            user = None
            response = urllib2.urlopen('https://api.github.com/user/emails?access_token=%s'%token)
            emaildata = json.loads(response.read())
            email = emaildata[0]
    except:
        request.session["alerts"].append(("alert-error","Error getting token from Github."))
        return redirect("index")   
    
    # Get the user and username. If the user is in the db, log it in. Otherwise,
    # create an account.
    
    
    # Log in or create the account.
    if user and not user.student.banned:
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        user.student.unread_since = user.student.last_login
        user.student.last_login = timezone.now()
        user.student.save()
        request.session["alerts"].append(("alert-success","Welcome back, %s!"%username))
        return redirect("index")
    elif user and user.student.banned:
        request.session["alerts"].append(("alert-error","""This account has
                                          been suspended. If you believe this
                                          is in error, please contact the site
                                          administrator."""))
        return redirect("index")
    elif settings.NO_NEW_ACCOUNTS:
        request.session["alerts"].append(("alert-error","""New account creation is not
                                          enabled at this time. Please try again in the
                                          future!"""))
        return redirect("index")
    else:
        user = User.objects.create_user(username, email, str(random.randint(100000000,999999999)))
        user.save()
        student = Student(user=user)
        student.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
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
    
    # A POST request means that the user has agreed to the terms of use.
    if request.method == "POST" and me:
        me.agreed = True
        me.save()
        request.session["alerts"].append(("alert-success","Thanks! Welcome to #8bitmooc!"))
        return redirect("index")
    
    # If they've already agreed, let them know.
    if me and me.agreed:
        request.session["alerts"].append(("alert-success","You have already agreed to the terms of use."))
    
    # Render the page.
    return render(request,
                  "terms_of_use.html",
                  {'alerts': request.session.pop('alerts', []) })


# The student profile page shows the avatar, links to their Github account,
# and shows progress and publications throughout the course.
@Student.permission
def user_profile(request, username):
    try: student = User.objects.get(username=username).student
    except exceptions.ObjectDoesNotExist:
        request.session["alerts"].append(("alert-error","That user does not exist."))
        return redirect("index")
    me = Student.from_request(request)
    
    if request.method == "POST":
        if me.ta and "ban" in request.POST:
            student.banned = not student.banned
            student.agreed = False
            student.save()
        return redirect("profile", username=username)
    
    return render(request,
                  "profile.html",
                  {'student': student,
                   'challenges': Challenge.show_for(student),
                   'published': CodeSubmission.objects.filter(published__gt=0, student=student).order_by('-timestamp'),
                   'alerts': request.session.pop('alerts', []) })


# Demo User
def create_demo_user(request):
    me = Student.from_request(request)
    if not settings.DEMO_MODE:
        request.session["alerts"].append(("alert-error","Demo users are not enabled at this time."))
        return redirect("index")
    
    username = "DemoUser%d"%len(Student.objects.all())
    user = User.objects.create_user(username, username+"@example.com", str(random.randint(100000000,999999999)))
    user.save()
    student = Student(user=user)
    student.save()
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    return redirect("index")

