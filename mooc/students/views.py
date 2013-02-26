# Create your views here.

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from lessons.models import Stage, World
from students.models import Student
from django.contrib.auth.models import User

import random


# Display a student's profile page.
def view_profile(request, username):
    try:
        student = Student.objects.get( user=User.objects.get(username=username) )
    except exceptions.ObjectDoesNotExist: raise Http404()

    return render( request, 'students_profile.html', {'student': student} )
    
