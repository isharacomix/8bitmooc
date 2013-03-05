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
from lessons.models import World

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
        lines = list(Chat.objects.filter(channel=world))
        count = len(lines)
        if state == count:
            log['state'] = state
            log['text'] = False
        else:
            text = []
            log['state'] = state + count - state
            for l in lines:
                text.append(l.content)
            log['text'] = text
    elif function == "send": 
        nickname = request.POST.get("nickname")
        message = request.POST.get("message")
        if message != "\n":
            C = Chat()
            C.author = student
            C.channel = world
            C.content = message
            C.save()
    
    chatlog_json = json.dumps(log)
    return HttpResponse(chatlog_json, content_type='application/json')

