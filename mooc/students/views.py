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

from students.forms import RegistrationForm, ProfileEditForm
from students.models import Student
from django.contrib.auth.models import User

import hashlib


def user_list(request):
    raise Http404()
def user_profile(request, username):
    raise Http404()
    

# If this is a POST request, we are trying to log in. If it is a GET request,
# we may be getting the page, unless the "verify" field is present, in which
# case we are doing e-mail verification.
def sign_in(request):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if me: return redirect("index")
    
    if request.method == "POST":
        if request.POST.get("sign-up")   == "sign-up": return redirect("sign-up")
        elif "username" in request.POST and "password" in request.POST:
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                if Student.objects.filter(user=user).exists():
                    login(request, user)
                    return redirect("index")
                else:
                    request.session["alerts"].append(("alert-error",
                                                      """This account has not yet
                                                      been activated. Please check
                                                      your e-mail for the activation
                                                      link."""))
                    return redirect("sign-in")
            else:
                request.session["alerts"].append(("alert-error",
                                                  """Incorrect username or
                                                  password."""))
                return redirect("sign-in")
        else: return redirect("sign-in")
    elif "key" in request.GET and "username" in request.GET:
        key = request.GET["key"]
        username = request.GET["username"]
        
        # Redirect to login if the user account does not exist or has already
        # been activated.
        try: user = User.objects.get(username=username)
        except exceptions.ObjectDoesNotExist: return redirect("sign-in")
        if Student.objects.filter(user=user).exists(): return redirect("sign-in")
        
        # Verify the hash and redirect if it doesn't match.
        if hashlib.sha256(username+settings.REGISTER_SALT).hexdigest() != key:
            return redirect("sign-in")
        
        # Assuming everything went well...
        S = Student( user=user )
        S.save()
        user.is_active = True
        user.save()
        request.session["alerts"].append(("alert-success",
                                          """Verification successful! You may
                                          now sign in!."""))
        return render(request, "sign-in.html", {'alerts': request.session.pop('alerts', []) })
    else:
        return render(request, "sign-in.html", {'alerts': request.session.pop('alerts', []) })


# If this is a POST request, we are trying to create an account.
def sign_up(request):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if me: return redirect("index")
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            u = User.objects.create_user(data['username'], data['email'], data['password1'])
            u.is_active = False
            u.is_admin = False
            u.save()
            request.session["alerts"].append(("alert-success",
                                              "Please check your e-mail for your verification link."))
            
            #TODO move this email to a file so that it's not so darn ugly.
            email = """
Howdy, %s!

You're almost all set for #8bitmooc - all that's left is to verify your
e-mail address. Please click on the following link to activate your
account!

http://%s/sign-up?username=%s&key=%s
            """%(u.username, settings.SITE_URL, u.username,
                 hashlib.sha256(u.username+settings.REGISTER_SALT).hexdigest())
            
            # Send an alert email to this individual.
            send_mail('[8bitmooc] Account Registration', email, 'bounces@8bitmooc.org',
                      [u.email], fail_silently=True)
            return redirect("sign-in")
        else:
            request.session["alerts"].append(("alert-failure",
                                              "There was an issue registering your account."))
            for e in form.non_field_errors():
                alerts.append( ("alert-error", e ) )
            return render( request, "sign-up.html", { "form":form,
                                                      'alerts': request.session.pop('alerts', []) } )
    else:
        form = RegistrationForm()
        return render(request, 'sign-up.html', {"form":form,
                                                'alerts': request.session.pop('alerts', []) })

    
# Sign the user out. Here I'm willing to avoid the 'student redirect' since
# we might have a logged in user anyway.
def sign_out(request):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    
    if me:
        logout(request)
        if "alerts" not in request.session: request.session["alerts"] = []
        request.session["alerts"].append( ("alert-success",
                                           "You have successfully signed out.") )
        return redirect("index")
    else:
        request.session["alerts"].append( ("alert-success",
                                           "You are already signed out.") )
        return redirect("sign-in")

