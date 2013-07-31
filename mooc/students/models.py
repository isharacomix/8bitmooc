# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core import exceptions
from django.shortcuts import render, redirect


# The Student model maintains extra information for verified Users in the
# system. Only Users that have corresponding Student models can log in.
class Student(models.Model):
    user            = models.OneToOneField(User,
                                           verbose_name="user",
                                           help_text="""The user that this student
                                           is connected to.""")
    ta              = models.BooleanField("Teaching Assistant",
                                          default=False,
                                          help_text="""When true, the student has
                                          access to grading interfaces.""")
    in_person       = models.BooleanField("In-Person Student",
                                          default=False,
                                          help_text="""True for students who are
                                          part of the in-person cohort.""")
    agreed          = models.BooleanField("Agree to Terms of Use",
                                          default=False,
                                          help_text="""True after the student
                                          agrees to the terms of use. Until they
                                          agree, they can't access pages.""")
    banned          = models.BooleanField("Is Banned",
                                          default=False,
                                          help_text="""If banned, the user can
                                          no longer log into the site.""")
    complete        = models.BooleanField("Complete",
                                          default=False,
                                          help_text="""Set to True when the
                                          student completes all of the
                                          challenges.""")
    joined          = models.DateTimeField("Joined",
                                           auto_now_add=True,
                                           help_text="""The time the student joined the
                                           MOOC.""")
    last_login      = models.DateTimeField("Last Login",
                                           null=True,
                                           blank=True,
                                           help_text="""The timestamp of the student's
                                           last visit.""")
    unread_since    = models.DateTimeField("Unread Since",
                                           null=True,
                                           blank=True,
                                           help_text="""The timestamp by which to
                                           measure unread posts.""")

    # When we represent the student, we put their TA tag on so that others can
    # recognize them.
    def __unicode__(self):
        return u"%s%s" % (self.user.username, u" [TA]" if self.ta else u"",)
    
    @property
    def username(self):
        return self.user.username
    
    @property
    def email(self):
        return self.user.email
    
    # Grab the Student out of the request. Returns None if a student is
    # not logged in. If redirect is True, then an error message will be
    # added.
    @staticmethod
    def from_request(request):
        if "alerts" not in request.session: request.session["alerts"] = []
        if request.user.is_authenticated():
            try:    return request.user.student
            except: return None
        else: return None


    # The @permission decorator will redirect to the index and post a message
    # requiring login if the user is anonymous and rejecting the user if he or
    # she is banned. The first argument in *args must be the request
    @staticmethod
    def permission(f):
        def new_f(*args, **kwargs):
            request = args[0]
            if "alerts" not in request.session: request.session["alerts"] = []
            me = Student.from_request(request)
            
            if not me:
                request.session["alerts"].append(("alert-error","Please log in to access this feature."))
                return redirect("index")
            elif me.banned:
                logout(request)
                if "alerts" not in request.session: request.session["alerts"] = []
                request.session["alerts"].append(("alert-error","""This account has
                                                  been suspended. If you believe this
                                                  is in error, please contact the site
                                                  administrator."""))
                return redirect("index")
            elif not me.agreed:
                return redirect("shrinkwrap")
            else:
                return f(*args, **kwargs)
        return new_f



# This is used for logging page visits.
class LogEntry(models.Model):
    student     = models.ForeignKey(Student,
                                    verbose_name="Student",
                                    null=True,
                                    blank=True,
                                    help_text="""The student being logged.""")
    timestamp   = models.DateTimeField("Timestamp",
                                       auto_now_add=True,
                                       help_text="""The time that the URL was
                                       accessed.""")
    url         = models.CharField("URL",
                                   max_length=200,
                                   help_text="""The URL that the student accessed.""")
    notes       = models.CharField("Notes",
                                   max_length=200,
                                   help_text="""Debug information.""")
    
    @staticmethod
    def log(request, notes=""):
        try: s = Student.from_request(request)
        except: s = None
        
        l = LogEntry(student=s,
                     url="%s:%s"%(request.method, request.path),
                     notes=notes)
        l.save()

    # Representation of the log entry.
    def __unicode__(self):
        return u"Log entry at %s" % (str(self.timestamp))



