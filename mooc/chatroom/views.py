# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from chatroom.models import Chat
from students.models import Student
from world.models import World

from gravatar.templatetags import gravatar

import json


# Even though there is no user-visible page for the chat room, we still need a
# URL dispatcher and view in order to handle the JSON output (kind of like the
# /rom/ URL).
def do_chat(request):
    try:
        student = Student.from_request(request)
        world = World.objects.get(shortname=request.POST.get("channel"))
    except exceptions.ObjectDoesNotExist:
        return HttpResponse(json.dumps({}), content_type='application/json')

    function = request.POST.get("function")
    log = {}
    
    if function == "getState":
        lines = list(Chat.objects.filter(channel=world))
        log['state'] = len(lines) 
    elif function == "update":
        state = int(request.POST.get("state"))
        lines = list(Chat.objects.filter(channel=world).reverse())
        
        count = len(lines)
        if state == count and request.POST.get("force") != "true":
            log['state'] = state
            log['messages'] = False
        else:
            messages = []
            log['state'] = state + count - state
            for l in lines:
                gimg = gravatar.gravatar_img_for_user(l.author.user, size=32).replace(' alt="',' alt="" class="media-object" title="')
                
                # Calculate the score (upvote-downvote)
                up = l.endorsed_by.all()
                dn = l.dismissed_by.all()
                upc = len(up)
                dnc = len(dn)
                score = upc-dnc
                
                # Convert it into a string (just for the plus sign).
                textscore = str(score)
                if score >= 0: textscore = "+"+textscore
                
                # If the user has already voted on this comment, don't let them
                # vote again, and don't let them vote on their own comment.
                comment_id = False
                if student != l.author and student not in up and student not in dn:
                    comment_id = l.id
                if score >= -1:
                    messages.append([l.author.username, gimg, l.content, str(l.timestamp), comment_id, textscore])
            log['messages'] =  messages
    elif function == "upvote": 
        try:
            l = Chat.objects.get(id=int(request.POST.get("comment")))
            l.endorsed_by.add(student)
            l.save()
            student.score += 1
            l.author.score += 3
            student.save()
            l.author.save()
        except: pass
    elif function == "downvote": 
        try:
            l = Chat.objects.get(id=int(request.POST.get("comment")))
            l.dismissed_by.add(student)
            l.save()
            student.score += 1
            student.save()
        except: pass
    elif function == "send": 
        message = request.POST.get("message")
        if message != "":
            C = Chat()
            C.author = student
            C.channel = world
            C.content = message[:140]
            C.save()
    
    chatlog_json = json.dumps(log)
    return HttpResponse(chatlog_json, content_type='application/json')

