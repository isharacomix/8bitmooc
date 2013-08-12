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
@Student.permission
def board_list(request):
    me = Student.from_request(request)
    
    # Get all of the boards that this student can read. Store them in the
    # board_pairs where they are paired with the number of new posts since their
    # last visit.
    board_triplets = []
    boards = DiscussionBoard.objects.all()
    for b in boards:
        if b.can_read(me):
            last_posts = b.discussiontopic_set.exclude(hidden=True)
            new_posts = len( last_posts.filter(last_active__gte=me.unread_since) )
            if len(last_posts) == 0: last_posts = [None]
            visible = False
            board_triplets.append( (b, last_posts[0], new_posts) )
    
    return render( request, "forums.html", {'boards': board_triplets,
                                            'alerts': request.session.pop('alerts', []) })
                   

# This displays all of the topics for the specified forum board.
@Student.permission
def view_board(request, category):
    me = Student.from_request(request)
    
    # First, try to get the board.
    try: board = DiscussionBoard.objects.get(slug=category)
    except exceptions.ObjectDoesNotExist: raise Http404()
    if not board.can_read(me): raise Http404()
    
    # Get the page number!
    page = 0
    pagination = 50
    if "page" in request.GET and request.GET["page"].isdigit():
        page = max(0,int(request.GET["page"])-1)
    
    # If this is a POST, we are creating a new topic. Redirect when finished.
    if request.method == "POST":
        if board.can_write(me):
            content = str(request.POST.get("content"))
            title = content[:100]+"..."
            if "title" in request.POST:
                title = request.POST["title"]
            
            t = DiscussionTopic()
            t.author = me
            t.board = board
            t.title = title
            t.save()
            
            p = DiscussionPost()
            p.topic = t
            p.author = me
            p.content = content
            p.save()
        
            return redirect( "thread", category=board.slug, thread=t.id )
        else:
            return redirect( "board", category=board.slug )
    
    # Get all of the topics, along with the last person who commented on them
    # and when that was.
    topic_tuples = []
    topics = DiscussionTopic.objects.filter(board=board)
    if not me.ta:
        topics = topics.filter(hidden=False)
    for t in topics[pagination*page:pagination*(page+1)]:
        posts = DiscussionPost.objects.filter(topic=t, hidden=False).order_by("-timestamp")
        count = len(posts)
        new = False
        if count == 0: posts = [None]
        else: new = ( posts[0].timestamp > me.unread_since )
        topic_tuples.append( (t,count,posts[0],new) )
    
    return render( request, "forum_topics.html", {'board': board,
                                                  'topics': topic_tuples,
                                                  'alerts': request.session.pop('alerts', []),
                                                  'page': page+1,
                                                  'pages': (len(topic_tuples)/pagination)+1,
                                                  'can_write': board.can_write(me) } )


# This displays a single thread on the specified board.
@Student.permission
def view_thread(request, category, thread):
    me = Student.from_request(request)
    
    # First, try to get the challenge, then thread.
    try:
        board = DiscussionBoard.objects.get(slug=category)
        topic = DiscussionTopic.objects.get(id=thread, board=board)
    except exceptions.ObjectDoesNotExist: raise Http404()
    if not board.can_read(me): raise Http404()
    
    
    # If this is a POST, we are either replying to someone or we are voting.
    # Manage permissions respectively and redirect.
    if request.method == "POST":
        if "hide" in request.POST and me.ta:
            try:
                p = DiscussionPost.objects.get(id=int(request.POST["hide"]))
                p.hidden = not p.hidden
                p.save()
            except: pass
        elif "topic" in request.POST and me.ta:
            if "lock" == request.POST.get("topic"):
                topic.locked = not topic.locked
            if "hide" == request.POST.get("topic"):
                topic.hidden = not topic.hidden
            topic.save()
        elif "content" in request.POST and board.can_write(me) and (not topic.locked):
            p = DiscussionPost()
            p.topic = topic
            p.author = me
            p.content = str(request.POST.get("content"))
            p.save()
            topic.save()
        return redirect( "thread", category=board.slug, thread=topic.id )
    
    # Get all of the posts. Start on the last page by default.
    pagination = 20
    posts = DiscussionPost.objects.filter(topic=topic)
    if not me.ta:
        post = posts.filter(hidden=False)
    pages = (len(posts)/pagination)+1
    page = pages-1
    if "page" in request.GET and request.GET["page"].isdigit():
        page = max(0,int(request.GET["page"])-1)
    
    return render( request, "forum_thread.html", {'board': board,
                                                  'topic': topic,
                                                  'posts': posts[pagination*page:pagination*(page+1)],
                                                  'alerts': request.session.pop('alerts', []),
                                                  'page': page+1,
                                                  'pages': pages,
                                                  'can_write': board.can_write(me) })

