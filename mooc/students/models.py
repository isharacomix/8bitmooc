# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core import exceptions


# The student represents each user in the Database. We use their username and
# e-mail from the User model, and don't worry so much about their real name
# and such. The primary purpose of the Student profile is to be associated with
# assignments, badges, and other submissions.
# Technically, teachers are also "students" in the course.
class Student(models.Model):
    user            = models.OneToOneField(User, verbose_name="user")
    
    # The friends list is a whitelist and the blocked list is a blacklist.
    # When someone is blocked by a substantial number of people, they are
    # considered auto-blocked (an idea from Extra Credits on maintaining
    # good community).
    friends         = models.ManyToManyField("Student", blank=True,
                        related_name='friends+',
                        help_text="Who is this user friends with? Friends "+
                                  "can see one anothers' progress and "+
                                  "prefer their posts to others.")
    blocked         = models.ManyToManyField("Student", blank=True,
                        related_name='blocked+',
                        help_text="Who is this user blocking?")    
    autoblocked     = models.BooleanField("autoblocked", default=False,
                        help_text="This is set where people who are not friends "+
                                  "with this user will not see their posts. Set "+
                                  "when many people block them (likely a troll).")
    TA              = models.BooleanField("TA", default=False,
                        help_text="This is set if the student is actually a TA.")
    
    # Personal profile settings (all of which are optional for the student).
    bio             = models.TextField("bio", blank=True,
                        help_text="The user's bio.")
    display_email   = models.BooleanField("display e-mail", default=False,
                        help_text="Display E-mail publicly?")
    twitter         = models.CharField("twitter", max_length=32, blank=True,
                        help_text="Twitter handle.")   
    
    # When we represent the student, we put their TA tag on so that others can
    # recognize them.
    def __unicode__(self):
        return u"%s%s" % (self.user.username, u" [TA]" if self.TA else u"")
    
    @property
    def username(self):
        return self.user.username
    
    @property
    def email(self):
        return self.user.email
    
    # Grab the Student out of the request. Raises exceptions.ObjectDoesNotExist
    # if the student does not exist.
    @staticmethod
    def from_request(request):
        if request.user.is_authenticated():
            return request.user.student
        else:
            raise exceptions.ObjectDoesNotExist()

