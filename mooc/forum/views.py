# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from students.models import Student, LogEntry
from forum.models import DiscussionBoard, DiscussionTopic, DiscussionPost
from django.contrib.auth.models import User


# This displays the forum boards that the student is allowed to see.
def board_list(request):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if not me:
        request.session["alerts"].append(("alert-error","Please sign in first."))
        return redirect("sign-in")   
    
    # Get all of the boards that this student can read. Store them in the
    # board_pairs where they are paired with the number of new posts since their
    # last visit.
    board_triplets = []
    for b in DiscussionBoard.objects.filter(restricted__lte=me.level):
        last_posts = b.discussiontopic_set.exclude(hidden=True)
        new_posts = len( last_posts.filter(last_active__gte=me.last_login) )
        if len(last_posts) == 0: last_posts = [None]
        board_triplets.append( (b, last_posts[0], new_posts) )
    
    return render( request, "forums.html", {'boards': board_triplets,
                                            'alerts': request.session.pop('alerts', []) })
                   

# This displays all of the topics for the specified forum board.
def view_board(request, name):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if not me:
        request.session["alerts"].append(("alert-error","Please sign in first."))
        return redirect("sign-in")   
    
    # First, try to get the board.
    try: board = DiscussionBoard.objects.get(slug=name)
    except exceptions.ObjectDoesNotExist: raise Http404()
    
    # If this is a POST, we are creating a new topic. Redirect when finished.
    
    return render( request, "forum_topics.html", {'alerts': request.session.pop('alerts', []) })


# This displays a single thread on the specified board.
def view_thread(request, name, thread):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if not me:
        request.session["alerts"].append(("alert-error","Please sign in first."))
        return redirect("sign-in")   
    
    # First, try to get the challenge, then thread.
    try:
        board = DiscussionBoard.objects.get(slug=name)
        topic = DiscussionThread.objects.get(id=thread, board=board)
    except exceptions.ObjectDoesNotExist: raise Http404()
    
    # If this is a POST, we are replying to someone.
    
    return render( request, "forum_thread.html", {'alerts': request.session.pop('alerts', []) })
    
