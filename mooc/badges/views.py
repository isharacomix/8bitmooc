from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from badges.models import Badge
from django.contrib.auth.models import User

import hashlib
import json


BADGE_SALT = "moocbadges"


# This function returns True if the specified User has the Badge.
def has_badge(badge, user):
    return user in badge.awarded_to.all()


# This prepares a list of all of the badges, displaying them on the badge
# list template.
def list_badges(request):
    return HttpResponse("test")


# This goes to the badge's home page, showing its description and requirements.
# If the logged-in user has successfully gotten this badge, this is where they
# go to add it to their badge backpack (handled by template).
def view_badge(request, badge):
    badge_object = Badge.objects.get(shortname=badge)
    return HttpResponse(badge)


# This returns a JSON string for the badge for the specified user if they
# have received the badge. This is public in order to support the verifier.
def assert_badge(request, badge, user):
    badge = Badge.objects.get(shortname=badge)
    user = User.objects.get(username=user)
    
    # If they have the badge, start making the JSON thing.
    if has_badge( badge, user ):
        badge_assertion_dict = {
          "recipient": "sha256$"+hashlib.sha256(user.email+BADGE_SALT).hexdigest(),
          "salt": BADGE_SALT,
          "evidence": "/badges/~"+user.username,
          "badge": {
            "version": "0.5.0",
            "name": badge.name,
            "image": badge.graphic,
            "description": badge.shortdesc,
            "criteria": "/badges/"+badge.shortname,
            "issuer": {
              "origin": "http://8bitmooc.org",
              "name": "8bitmooc",
              "org": "8bitmooc",
              "contact": "admin@8bitmooc.org"
           }
          }
        }
        
        badge_assertion_json = json.dumps(badge_assertion_dict)
        return HttpResponse(badge_assertion_json, mimetype='application/json')
    
    # Otherwise return an empty page.
    else:
        raise Http404()

