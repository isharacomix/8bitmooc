# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect
from django.template.defaultfilters import slugify

from students.models import Student, LogEntry
from projects.models import Project, ProjectCommit
from django.contrib.auth.models import User

from nes import assembler
from nes.views import get_rom
from nes.models import Pattern, Game

import random
import difflib


# The user can filter out projects based on whether they work on them, the
# project needs help, or they have favorited it.
def project_list(request):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if not me:
        request.session["alerts"].append(("alert-error","Please sign in first."))
        return redirect("sign-in")   
    
    # Retrieve GET parameters.
    filt = request.GET.get("filter")
    page = request.GET.get("page")
    if page and page.isdigit(): page = max(0, int(page)-1)
    else: page = 0
    pagination = 50
    
    # If we get a POST request, we create a new project.
    if request.method == "POST":
        name = str(request.POST.get("name"))
        if len(Project.objects.filter(name="name")) > 0:
            request.session["alerts"].append(("alert-error",
                                              """A project with that name already
                                              exists. Please choose a different
                                              name."""))
            return redirect("project_list")
        else:
            p = Project()
            p.name = name
            p.owner = me
            p.save()
            return redirect("project", id=p.id)
    
    # Filter the project list based on the GET filter parameter.
    project_list = []
    if filt == "help":
        project_list += list(Project.objects.filter(is_public=True, help_wanted=True))
    elif filt == "watch":
        project_list += list(me.watches.filter(is_public=True))
    elif filt == "all":
        project_list += list(me.owns.filter(is_public=False))
        project_list += list(me.works_on.filter(is_public=False))
        project_list += list(Project.objects.filter(is_public=True))
    else:
        project_list += list(me.owns.all())
        project_list += list(me.works_on.all())
        filt = "mine"
    project_list = project_list[page*pagination:(page+1)*pagination]
    
    # TODO: Create the spotlight.
    
    
    return render( request, "project_list.html", {'projects':project_list,
                                                  'alerts': request.session.pop('alerts', []),
                                                  'page': page+1,
                                                  'pages': (len(project_list)/pagination)+1,
                                                  'filter': filt } )


# This is the screen where students can edit projects and see each others' code.
def view_project(request, id):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if not me:
        request.session["alerts"].append(("alert-error","Please sign in first."))
        return redirect("sign-in")   
    
    # Make sure the game exists and we are allowed to see it.
    try: project = Project.objects.get(id=id)
    except exceptions.ObjectDoesNotExist: return redirect("project_list")
    if not project.is_public and (me != project.owner and me not in project.team.all()):
        return redirect("project_list")
    
    # If we have a POST request, then we need to save the changes we make.
    # We need to come up with a way to improve working together on projects.
    is_owner = (me == project.owner)
    can_edit = (is_owner or me in project.team.all())
    if request.method == "POST":
        if can_edit:
            old_code = project.code
            project.code = str(request.POST.get("code"))
            commit = ProjectCommit()
            commit.author = me
            commit.project = project
            commit.diff = ""
            for d in difflib.unified_diff( old_code.splitlines(), project.code.splitlines()):
                commit.diff += d+"\n"
            commit.save()
            try: project.pattern = Pattern.objects.get(name=request.POST.get("pattern"))
            except exceptions.ObjectDoesNotExist: project.pattern = None
            project.save()
        if "watch" in request.POST:
            if request.POST["watch"] == "true" and me not in project.watched_by.all():
                project.watched_by.add(me)
            elif request.POST["watch"] == "false" and me in project.watched_by.all():
                project.watched_by.remove(me)
            project.save()
        if "public" in request.POST and is_owner:
            if request.POST["public"] == "no":
                project.is_public = False
                project.help_wanted = False
            elif request.POST["public"] == "yes":
                project.is_public = True
                project.help_wanted = False
            elif request.POST["public"] == "help":
                project.is_public = True
                project.help_wanted = True
            project.save()
        if "fork" in request.POST:
            name = str(request.POST.get("title"))
            if len(Project.objects.filter(name="title")) > 0:
                request.session["alerts"].append(("alert-error",
                                                  """A project with that name already
                                                  exists. Please choose a different
                                                  name."""))
                return redirect("project_list")
            else:
                p = Project()
                p.name = name
                p.owner = me
                p.save()
                return redirect("project", id=p.id)
        if "adduser" in request.POST and is_owner:
            try:
                newguy = Student.objects.get( user=User.objects.get(username=request.POST.get("username")) )
                project.team.add(newguy)
                project.save()
            except exceptions.ObjectDoesNotExist:
                request.session["alerts"].append(("alert-error",
                                                  "Could not find the specifed user. Did you type it in wrong?"))
        if "removeuser" in request.POST and is_owner:
            try:
                newguy = Student.objects.get( user=User.objects.get(username=request.POST.get("username")) )
                if newguy in project.team.all(): project.team.remove(newguy)
                project.save()
            except exceptions.ObjectDoesNotExist:
                request.session["alerts"].append(("alert-error",
                                                  "Could not find the specifed user. Did you type it in wrong?"))
        
        good = assembler.assemble_and_store(request, slugify(project.name), project.code, project.pattern)
        if "download" in request.POST:
            return redirect("rom")
        elif "publish" in request.POST:
            project.version += 1
            project.save()
            g = Game()
            g.title = project.name + (" (version %d)"%project.version if project.version > 1 else "")
            g.code = project.code
            g.pattern = project.pattern
            g.description = str(request.POST.get("description"))
            g.save()
            g.authors.add(project.owner)
            for t in project.team.all():
                g.authors.add(t)
            g.save()
            return redirect("play", id=g.id)
        else:
            return redirect("project", id=project.id)
    
    # If we decided we wanted to download the code then we download it.
    return render(request, "project.html", {'alerts': request.session.pop('alerts', []),
                                            'project': project,
                                            'patterns': Pattern.objects.all(),
                                            'can_edit': can_edit} )
    
    
