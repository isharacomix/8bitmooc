# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect
from django.template.defaultfilters import slugify

from students.models import Student
from challenges.models import ChallengeResponse
from nes.models import Game, Pattern

from nes import assembler
import difflib


# The playground is just an assembler web page that students can use whether
# or not they are logged in. If they are logged in then the playground loads
# their last submission.
def view_playground(request):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    
    # Compile the code and save it in the database.
    good = False
    pattern = None
    if request.method == "POST":
        try: old = ChallengeResponse.objects.filter(student=me).order_by('-timestamp')[0]
        except: old = None
        
        # Get code from the POST request.
        code = request.POST.get("code") if "code" in request.POST else ""
        try: pattern = Pattern.objects.get(name=str(request.POST.get("pattern")))
        except: pass
        
        # Save this in the database whether it compiles or not.
        CR = ChallengeResponse()
        CR.student = me
        CR.code = code
        CR.save()
        
        # Convert the last code submission into a diff image.
        if old:
            old.parent = CR
            old_code = old.code
            old.code = ""
            for d in difflib.unified_diff( old_code.splitlines(), CR.code.splitlines()):
                old.code += d + "\n"
            old.save()

        good = assembler.assemble_and_store(request, "playground", code, pattern)
        
        if "download" in request.POST and good:
            return redirect("rom")
        else:
            return redirect("playground")
    
    # Render the page.
    code = "; put default code here one day"
    if 'rom_code' in request.session:
        code = request.session["rom_code"]
        pattern = request.session.get("rom_pattern")
    elif 'source' in request.GET:
        try:
            game = Game.objects.get(id=int(request.GET['source']))
            code = game.code
            pattern = game.pattern
        except: pass
    elif me:
        subs = ChallengeResponse.objects.filter(student=me).order_by('-timestamp')
        if len(subs) > 0: code = subs[0].code
    return render(request, "playground.html", {'alerts': request.session.pop('alerts', []),
                                               'pattern': pattern,
                                               'patterns': Pattern.objects.all(),
                                               'code': code} )


# This displays a list of games that people can play, organized by popularity.
def games_list(request):
    page = 0
    pagination = 200
    if "page" in request.GET and request.GET["page"].isdigit():
        page = max(0,int(request.GET["page"])-1)
    game_list = Game.objects.all().order_by("-hits")[pagination*page:pagination*(page+1)]
    return render(request, "arcade_list.html", {'games': game_list,
                                                'page': page+1,
                                                'pages': (len(game_list)/pagination)+1 } )


# This shows the list of all of the sprites available.
def sprite_list(request):
    return render(request, "sprite_list.html", {'patterns': Pattern.objects.all()})


# The arcade is like a playground with even less fun. You can view the source
# code of any such game, though, so that's a good thing.
def play_game(request, id):
    try: game = Game.objects.get(id=id)
    except exceptions.ObjectDoesNotExist: return redirect("arcade")
    
    good = assembler.assemble_and_store(request, slugify(game.title), game.code, game.pattern)
    request.session.pop('alerts', [])
    
    game.hits += 1
    game.save()
    
    # Now we can display the code to the user.
    if not good:
        return redirect("arcade")
    elif "download" in request.GET:
        return redirect("rom")
    else:
        return render(request, "arcade.html", {'game': game} )


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


