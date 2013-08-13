# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect
from django.template.defaultfilters import slugify

import difflib

from students.models import Student
from nes.models import Pattern, CodeSubmission
from nes import assembler



# The playground is just an assembler web page that students can use whether
# or not they are logged in. If they are logged in then the playground loads
# their last submission.
def view_playground(request):
    me = Student.from_request(request)
    
    # Compile the code and save it in the database.
    good = False
    pattern = None
    name = ""
    if request.method == "POST":
        try: old = CodeSubmission.objects.filter(student=me, challenge=None).order_by('-timestamp')[0]
        except: old = None
        
        # Get code from the POST request.
        name = slugify(request.POST.get("name") if request.POST.get("name") else "untitled")[:32]
        code = request.POST.get("code") if request.POST.get("code") else ""
        try: pattern = Pattern.objects.get(name=str(request.POST.get("pattern")))
        except: pattern = None
        
        # Save this in the database whether it compiles or not.
        CR = CodeSubmission()
        CR.name = name
        CR.student = me
        CR.code = code
        CR.pattern = pattern
        CR.save()
        
        good = assembler.assemble_and_store(request, name, code, pattern)
        publish = False
        if "publish" in request.POST and me and not me.banned and good:
            publish = True
        
        # Convert the last code submission into a diff image, but only save it
        # if the diff is actually smaller than the full code.
        if old and old.published == 0:
            old.parent = CR
            old_code = old.code
            old.code = ""
            for d in difflib.unified_diff( old_code.splitlines(), CR.code.splitlines()):
                old.code += d + "\n"
            if len(old.code) < len(old_code):
                old.save()
        
        # Redirect based on which button was clicked.
        if publish:
            CR.published = len(CodeSubmission.objects.filter(published__gt=0))+1
            CR.save()
            return redirect("playground")
        elif "download" in request.POST and good:
            return redirect("rom")
        else:
            return redirect("playground")
    
    # Render the page.
    code = ""
    if 'rom_code' in request.session:
        code = request.session["rom_code"]
        pattern = request.session.get("rom_pattern")
        name = str(request.session.get("rom_name"))
    elif me:
        subs = CodeSubmission.objects.filter(student=me, challenge=None).order_by('-timestamp')
        if len(subs) > 0:
            code = subs[0].code
            name = subs[0].name
    
    # Get recently published games.
    recent = CodeSubmission.objects.filter(published__gt=0).order_by('-timestamp')
    return render(request, "playground.html", {'name': name,
                                               'pattern': pattern,
                                               'patterns': Pattern.objects.all(),
                                               'code': code,
                                               'recently_published': recent[:25],
                                               'alerts': request.session.pop('alerts', []) } )


# This loads a previously published game.
def view_published(request, id):
    if id > 0:
        try:
            c = CodeSubmission.objects.get(published=id)
            assembler.assemble_and_store(request, c.name, c.code, c.pattern)
        except: pass
    return redirect("playground")

# The get_rom view simply returns the current ROM that is in the session
# variables.
def get_rom(request):
    name = "untitled"
    if "rom_name" in request.session: name = request.session["rom_name"]
    if "rom" in request.session and request.session["rom"] != "":
        response = HttpResponse(request.session["rom"], content_type='application/x-nes-rom')
        response['Content-Disposition'] = 'attachment; filename=%s.nes'%name
        return response 
    else:
        raise Http404()


# This shows the list of all of the sprites available.
def sprite_list(request):
    return render(request, "sprites.html", {'patterns': Pattern.objects.all()})



