# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.core.mail import send_mail
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from world.models import Stage, World
from students.models import Student
from students.forms import RegistrationForm, ProfileEditForm
from django.contrib.auth.models import User

import hashlib
import random


# Display a student's profile page.
def view_profile(request, username):
    try:
        student = Student.objects.get( user=User.objects.get(username=username) )
    except exceptions.ObjectDoesNotExist: raise Http404()
    
    # Take care of friending and profile editing.
    alerts = []
    form = ProfileEditForm( {'bio':student.bio,
                             'email':student.display_email,
                             'twitter':student.twitter,
                             'website':student.website} )
    
    autoshow = False
    if request.method == 'POST':
        try: me = Student.from_request(request)
        except exceptions.ObjectDoesNotExist: return redirect("login")
        
        if 'editprofile' in request.POST and me == student:
            form =  ProfileEditForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                student.bio = data['bio']
                student.display_email = data['email']
                student.twitter = data['twitter']
                student.website = data['website']
                student.save()
            else:
                autoshow = True
        
        if 'friend' in request.POST:
            # send the new friend an alert
            if student not in me.friends.all():
                me.friends.add(student)
                me.save()
                alerts.append( {"tags":"alert-success",
                                "content":"Friend request sent."} )
        if 'unfriend' in request.POST or 'block' in request.POST:
            if student in me.friends.all():
                me.friends.remove(student)
                me.save()
                alerts.append( {"tags":"alert-success",
                                "content":"Removed from friends list."} )
        if 'block' in request.POST:
            if student not in me.blocked.all():
                me.blocked.add(student)
                me.save()
                alerts.append( {"tags":"alert-success",
                                "content":"User blocked."} )
        if 'unblock' in request.POST or 'friend' in request.POST:
            if student in me.blocked.all():
                me.blocked.remove(student)
                me.save()
                alerts.append( {"tags":"alert-success",
                                "content":"User unblocked."} )
        
    
    # We only want to get the neweest of each game.
    games = {}
    for g in student.assemblychallengeresponse_set.filter(public=True,
                                                          challenge=None).reverse():
        if g.name not in games:
            games[g.name] = g

    return render( request, 'students_profile.html', {'student': student,
                                                      'games': games.values(),
                                                      'alerts': alerts,
                                                      'form':form,
                                                      'autoshow':autoshow} )


# This logs a user in, provided the password and stuff is right. :P
def login_page(request):
    if request.user.is_authenticated():
        return redirect("dashboard")
    elif "key" in request.GET and "username" in request.GET:
        key = request.GET["key"]
        username = request.GET["username"]
        
        # Redirect to login if the user account does not exist or has already
        # been activated.
        try: user = User.objects.get(username=username)
        except exceptions.ObjectDoesNotExist: return redirect("login")
        if Student.objects.filter(user=user).exists(): return redirect("login")
        
        # Verify the hash and redirect if it doesn't match.
        if hashlib.sha256(username+settings.REGISTER_SALT).hexdigest() != key:
            return redirect("login")
        
        # Assuming everything went well...
        S = Student( user=user )
        S.save()
        user.is_active = True
        user.save()
        return render( request, "login.html", {"alerts":[{"tags":"alert-success",
                                "content":"Account creation successful! You may now log in."}]} )
    elif request.method == 'POST':
        if request.POST.get("register") == "register": return redirect("register")
        if request.POST.get("login") == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                if Student.objects.filter(user=user).exists():
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
        alerts = {}
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            u = User.objects.create_user(data['username'], data['email'], data['password1'])
            u.is_active = False
            u.is_admin = False
            u.save()
            alerts = [{"tags":"alert-success",
                       "content":"Please check e-mail for your registration link."}]
            
            #TODO move this email to a file so that it's not so darn ugly.
            email = """
Howdy, %s!

You're almost all set for #8bitmooc - all that's left is to verify your
e-mail address. Please click on the following link to activate your
account!

http://%s/login?username=%s&key=%s
            """%(u.username, settings.SITE_URL, u.username,
                 hashlib.sha256(u.username+settings.REGISTER_SALT).hexdigest())
            
            # Send an alert email to this individual.
            send_mail('[8bitmooc] Account Registration', email, 'bounces@8bitmooc.org',
                      [u.email], fail_silently=True)
            return render( request, "return_to_home.html", {"alerts":alerts} )
        else:
            alerts = [{"tags":"alert-error",
                       "content":"There was an issue registering your account."}]
            for e in form.non_field_errors():
                alerts.append( {"tags":"alert-error", "content":e } )
            return render( request, "register.html", { "form":form, 
                                                       "alerts":alerts} )
    else:
        form = RegistrationForm()
        return render(request, 'register.html', {"form":form})
    

# This is just a logout page that logs the user out and goes to the "return to home"
# landing page.
def logout_page(request):
    if request.user.is_authenticated():
        logout(request)
        return render( request, "return_to_home.html", {"alerts":[{"tags":"alert-success",
                                                      "content":"You have successfully logged out."}]} )
    else:
        return redirect("login")
    

