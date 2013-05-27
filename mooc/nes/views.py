# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from students.models import Student
from challenges.models import ChallengeResponse
from nes.models import Game

from nes import assembler


# The playground is just an assembler web page that students can use whether
# or not they are logged in. If they are logged in then the playground loads
# their last submission.
def view_playground(request):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    
    # Compile the code and save it in the database.
    good = False
    if request.method == "POST":
        code = request.POST.get("code") if "code" in request.POST else ""
        
        # Save this in the database whether it compiles or not.
        CR = ChallengeResponse()
        CR.student = me
        CR.code = code
        CR.save()

        good = assembler.assemble_and_store(request, code)
    
    # If we decided we wanted to download the code then we download it.
    if "download" in request.POST and good:
        return get_rom(request, challenge.slug)
    else:
        code = "; put default code here one day"
        if 'code' in request.POST: code = request.POST['code']
        elif 'source' in request.GET:
            try: code = Game.objects.get(id=int(request.GET['source'])).code
            except: pass
        elif me:
            subs = ChallengeResponse.objects.filter(student=me).order_by('-timestamp')
            if len(subs) > 0: code = subs[0].code
        return render(request, "playground.html", {'alerts': request.session.pop('alerts', []),
                                                   'code': code} )


# This displays a list of games that people can play, organized by popularity.
def games_list(request):
    page = 0
    if "page" in request.GET and request.GET["page"].isdigit():
        page = int(request.GET["page"])
    game_list = Game.objects.all().order_by("-hits")[200*page:200*(page+1)]
    return render(request, "arcade_list.html", {'games': game_list,
                                                'page': page,
                                                'last_page': (not len(game_list)==200) } )


# The arcade is like a playground with even less fun. You can view the source
# code of any such game, though, so that's a good thing.
def play_game(request, id):
    try: game = Game.objects.get(id=id)
    except exceptions.ObjectDoesNotExist: return redirect("arcade")
    
    good = assembler.assemble_and_store(request, game.code, game.pattern)
    request.session.pop('alerts', [])
    
    game.hits += 1
    game.save()
    
    # Now we can display the code to the user.
    if not good:
        return redirect("arcade")
    elif "download" in request.GET:
        return get_rom(request, "game%d"%int(id))
    else:
        return render(request, "arcade.html", {'title': game.title,
                                               'id': game.id,
                                               'authors': game.authors.all() } )


# The get_rom view simply returns the current ROM that is in the session
# variables.
def get_rom(request, name="untitled"):
    if 'name' in request.GET: name = request.GET['name']
    
    if "rom" in request.session and request.session["rom"] != "":
        response = HttpResponse(request.session["rom"], content_type='application/x-nes-rom')
        response['Content-Disposition'] = 'attachment; filename=%s.nes'%name
        return response 
    else:
        raise Http404()


