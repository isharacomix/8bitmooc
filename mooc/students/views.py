# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect


def user_list(request):
    raise Http404()
def user_profile(request, username):
    raise Http404()
def sign_in(request):
    raise Http404()
def sign_up(request):
    raise Http404()
def sign_out(request):
    raise Http404()


