from django.conf import settings
from django.core import exceptions
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from badges.models import Badge
from students.models import Student
from django.contrib.auth.models import User

import hashlib
import json
import os


# Here are the constants needed to do things.
ISSUER_DOMAIN = "http://8bitmooc.org"
ISSUER_NAME = "8bitmooc"
ISSUER_ORG = "8bitmooc"
ISSUER_CONTACT = "admin@8bitmooc.org"


# This prepares a list of all of the badges, displaying them on the badge
# list template.
def list_badges(request):
    badge_list = Badge.objects.all()
    for b in badge_list:
        try: b.check = True if b.held_by( Student.from_request(request) ) else False
        except exceptions.ObjectDoesNotExist: b.check = False
    
    return render( request, "badge_list.html", {"badge_list":badge_list} )


# This goes to the badge's home page, showing its description and requirements.
# If the logged-in user has successfully gotten this badge, this is where they
# go to add it to their badge backpack (handled by template).
def view_badge(request, badge):
    
    # If the badge doesn't exist, take the user to the list.
    try: badge = Badge.objects.get(shortname=badge)
    except exceptions.ObjectDoesNotExist: return redirect( "badge_list" )
    
    # Determine if the User has the badge.
    try: awarded = True if badge.held_by(Student.from_request(request)) else False
    except exceptions.ObjectDoesNotExist: awarded = False
    
    # To embed the add-to-backpack button in your model, use the following
    # script: be sure you check to see if the user is authenticated.
    #   <script src="http://beta.openbadges.org/issuer.js"></script>
    #   <script type="text/javascript">
    #   OpenBadges.issue(["{{ domain }}{% url badge_assert user=user.username badge=badge.shortname %}"],function(errors, successes) {});
    #   </script>
    
    return render( request, "badge_details.html", {"badge":badge,
                                                   "awarded":awarded,
                                                   "domain":ISSUER_DOMAIN} )


# This returns a JSON string for the badge for the specified user if they
# have received the badge. This is public in order to support the verifier.
def assert_badge(request, badge, user):
    try:
        badge = Badge.objects.get(shortname=badge)
        student = Student.objects.get( user=User.objects.get(username=user) )
    except exceptions.ObjectDoesNotExist: raise Http404()
    
    # If they have the badge, start making the JSON thing.
    salt = settings.BADGE_SALT + '.' + badge.shortname
    if badge.held_by( student ):
        badge_assertion_dict = {
          "recipient": "sha256$"+hashlib.sha256(student.user.email+salt).hexdigest(),
          "salt": salt,
          "evidence": ISSUER_DOMAIN+"/~"+student.user.username,
          #"expires": "2013-06-01",
          #"issued_on": "2011-06-01",
          "badge": {
            "version": "0.5.0",
            "name": badge.name,
            "image": ISSUER_DOMAIN + settings.STATIC_URL + "img/" + badge.graphic +".png",
            "description": badge.shortdesc,
            "criteria": ISSUER_DOMAIN + "/badges/"+badge.shortname,
            "issuer": {
              "origin": ISSUER_DOMAIN,
              "name": ISSUER_NAME,
              "org": ISSUER_ORG,
              "contact": ISSUER_CONTACT
           }
          }
        }
        
        badge_assertion_json = json.dumps(badge_assertion_dict)
        return HttpResponse(badge_assertion_json, mimetype='application/json')
    
    # Otherwise return an empty page. This is not a page for humans, so no need
    # to make it pretty.
    else:
        raise Http404()

