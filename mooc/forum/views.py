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
    boards = DiscussionBoard.objects.all()
    if not me.ta: boards = boards.filter(restricted__lte=me.level)
    for b in boards:
        last_posts = b.discussiontopic_set.exclude(hidden=True)
        new_posts = len( last_posts.filter(last_active__gte=me.unread_since) )
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
    if board.restricted > me.level and not me.ta: raise Http404()
    
    # Get the page number!
    page = 0
    pagination = 200
    if "page" in request.GET and request.GET["page"].isdigit():
        page = max(0,int(request.GET["page"])-1)
    
    # If this is a POST, we are creating a new topic. Redirect when finished.
    if request.method == "POST" and (me.level >= board.wrestricted or me.ta):
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
        
        return redirect( "thread", name=board.slug, thread=t.id )
    
    # Get all of the topics, along with the last person who commented on them
    # and when that was.
    topic_tuples = []
    for t in DiscussionTopic.objects.filter(hidden=False, board=board)[pagination*page:pagination*(page+1)]:
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
    if not me.ta and (topic.hidden or board.restricted > me.level): raise Http404()
    
    # If this is a POST, we are either replying to someone or we are voting.
    # Manage permissions respectively and redirect.
    if request.method == "POST":
        if "thread" in request.POST:
            p = DiscussionPost()
            p.topic = topic
            p.author = me
            p.content = str(request.POST.get("content"))
            p.save()
            topic.save()
        elif "upvote" in request.POST or "downvote" in request.POST:
            upvote = True
            if "downvote" in request.POST: upvote = False
            p_id = request.POST["upvote" if upvote else "downvote"]
            if p_id.isdigit() and (me.modpoints > 0 or me.ta):
                p = DiscussionPost.objects.get(id=int(p_id))
                if upvote: p.upvotes += 1
                else:      p.downvotes += 1
                request.session["alerts"].append(("alert-success","Post %s."%("upvoted" if upvote else "downvoted")))
                LogEntry.log(request, "Thread %s"%("upvoted" if upvote else "downvoted"))
                p.save()
                me.modpoints -= 1
                me.award_xp(1)
                me.save()
        return redirect( "thread", name=board.slug, thread=topic.id )
    
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
    
