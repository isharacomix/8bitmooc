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

from students.forms import RegistrationForm, ProfileEditForm
from students import forms
from students.models import Student
from django.contrib.auth.models import User

import hashlib


# Display a list of all users in the course, ranked by their Levels and
# Experience Points.
def user_list(request):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if not me:
        request.session["alerts"].append(("alert-error","Please sign in first."))
        return redirect("sign-in")
    
    # Get all of the GET parameters.
    filt = request.GET.get("filter")
    page = request.GET.get("page")
    if page and page.isdigit(): page = max(0, int(page)-1)
    else: page = 0
    pagination = 99
    
    # Get the students
    student_list = []
    if filt == "teachers":
        student_list += list(Student.objects.filter(ta=True).order_by("-level","-xp"))
    elif filt == "collab":
        student_list += list(me.collaborators()) 
    elif filt == "blocked":
        student_list += list(me.student_set.all()) 
    else:
        student_list += list(Student.objects.all().order_by("-level","-xp"))
        filt = "all"
    
    # Break the students into three columns
    l1,l2,l3 = [],[],[]
    for s in student_list[pagination*page:pagination*(page+1)]:
        if len(l2) > len(l3): l3.append(s)
        elif len(l1) > len(l2): l2.append(s)
        else: l1.append(s)
    
    return render(request, "user_list.html", {"user_columns": (l1,l2,l3),
                                              "page": page+1,
                                              'pages': (len(student_list)/pagination)+1,
                                              "filter": filt } )
    

# Display a fancy user profile including stuff like their progress in the
# course and their collaborators on projects.
def user_profile(request, username):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if not me:
        request.session["alerts"].append(("alert-error","Please sign in first."))
        return redirect("sign-in")
    try: student = Student.objects.get( user=User.objects.get(username=username) )
    except: return redirect("user_list")
    
    # If we are doing a POST, then let's affect the output a bit.
    form = ProfileEditForm( {"bio": me.bio, "twitter": me.twitter, "email": me.public_email} )
    if request.method == "POST":
        form = ProfileEditForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            me.bio = data["bio"]
            me.public_email = data["email"]
            me.twitter = data["twitter"]
            me.save()
            return redirect( "profile", username=me.username )
        else:
            request.session["alerts"].append(("alert-error",
                                              "There were some issues with your profile update."))
            for e in form.non_field_errors():
                alerts.append( ("alert-error", e ) )
    
    # Render the magic.
    projects = list(me.owns.all())+list(me.works_on.all())
    return render(request, "user_profile.html", {"student": student,
                                                 "collaborators": student.collaborators(),
                                                 "projects": projects,
                                                 "form": form,
                                                 'alerts': request.session.pop('alerts', []) } )
    

# If this is a POST request, we are trying to log in. If it is a GET request,
# we may be getting the page, unless the "verify" field is present, in which
# case we are doing e-mail verification.
def sign_in(request):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if me: return redirect("index")
    
    if request.method == "POST":
        if request.POST.get("sign-up") == "sign-up": return redirect("sign-up")
        elif "username" in request.POST and "password" in request.POST:
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                if Student.objects.filter(user=user).exists():
                    login(request, user)
                    s = user.student
                    s.last_login = s.this_login
                    s.this_login = timezone.now()
                    if s.last_login is None:
                        s.last_login = s.this_login
                    if s.last_login.day != s.this_login.day:
                        s.modpoints = s.level
                    s.save()
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
    
    form = RegistrationForm()
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

