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
    
    # Get the page number!
    page = 0
    pagination = 200
    if "page" in request.GET and request.GET["page"].isdigit():
        page = max(0,int(request.GET["page"])-1)
    
    # If this is a POST, we are creating a new topic. Redirect when finished.
    
    # Get all of the topics, along with the last person who commented on them
    # and when that was.
    topic_tuples = []
    for t in DiscussionTopic.objects.filter(hidden=False, board=board)[pagination*page:pagination*(page+1)]:
        posts = DiscussionPost.objects.filter(topic=t, hidden=False).order_by("-timestamp")
        count = len(posts)
        new = False
        if count == 0: posts = [None]
        else: new = ( posts[0].timestamp > me.last_login )
        topic_tuples.append( (t,count,posts[0],new) )
    
    return render( request, "forum_topics.html", {'board': board,
                                                  'topics': topic_tuples,
                                                  'alerts': request.session.pop('alerts', []),
                                                  'page': page+1,
                                                  'pages': (len(topic_tuples)/pagination)+1 } )


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
        topic = DiscussionTopic.objects.get(id=thread, board=board)
    except exceptions.ObjectDoesNotExist: raise Http404()
    
    # If this is a POST, we are replying to someone. Post the string and
    # redirect.
    
    # Get all of the posts. Start on the last page by default.
    pagination = 20
    posts = DiscussionPost.objects.filter(hidden=False, topic=topic)
    pages = (len(posts)/pagination)+1
    page = pages-1
    if "page" in request.GET and request.GET["page"].isdigit():
        page = max(0,int(request.GET["page"])-1)
    
    return render( request, "forum_thread.html", {'board': board,
                                                  'topic': topic,
                                                  'posts': posts[pagination*page:pagination*(page+1)],
                                                  'alerts': request.session.pop('alerts', []),
                                                  'page': page+1,
                                                  'pages': pages })
    
