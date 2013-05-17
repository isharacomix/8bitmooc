# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from world.models import Stage, World, Achievement
from students.models import Student
from students.forms import RegistrationForm, ProfileEditForm
from django.contrib.auth.models import User

import hashlib
import random
import feedparser


# Display the website index. We have to parse the blog feed for this.
def view_index(request):
    try:    feed = feedparser.parse(r'http://blog.8bitmooc.org/rss').entries[:3]
    except: feed = []
    
    # TODO - filter out worlds that the user should not be able to see yet.
    worlds = []
    try:
        student = Student.from_request(request)
        achievements = student.achievement_set.all()
        completed = student.stage_set.all()
        world_candidates = World.objects.all()
        
        for w in world_candidates:
            students = list(Student.objects.filter(recent_world=w).exclude(id=student.id))
            to_stages = Stage.objects.filter(world=w)
            to_achievements = Achievement.objects.filter(won_in=w)
            points = 0
            for a in to_achievements:
                if a in achievements: points += 1
            for a in to_stages:
                if a in completed: points += 1
            total = len(to_stages)+len(to_achievements)
            random.shuffle(students)
            if w.prereq is None or w.prereq in achievements:
                worlds.append( (w,len(students), students[:4], int(100.*points/total)) )
    except: pass
    
    return render( request, 'index.html', {'feed': feed,
                                           "worlds": worlds } )

def view_privacy(request):
    return render( request, 'privacy.html' )
def view_terms(request):
    return render( request, 'terms.html' )

