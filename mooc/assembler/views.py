# Create your views here.

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from textbook.models import Page
from students.models import Student

import random


def view_playground(request):
    return render( request, "assembler_playground.html")
    
    


# This will take the post request and store it in the DB.
#def do_playground()

