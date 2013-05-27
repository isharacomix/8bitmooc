# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core import exceptions


# The Student model maintains extra information for verified Users in the
# system. Only Users that have corresponding Student models can log in.
class Student(models.Model):
    user            = models.OneToOneField(User,
                                           verbose_name="user",
                                           null=True,
                                           help_text="""
                                           The user that this student is
                                           connected to. If None, this student
                                           has not confirmed their registration.""")
    xp              = models.IntegerField("Experience Points",
                                          default=0,
                                          help_text="""
                                          The student's current experience
                                          points. When this goes up, the student
                                          gains levels. Resets to 0 when a level
                                          is gained.""")
    level           = models.IntegerField("Level",
                                          default=1,
                                          help_text="""
                                          The student's current experience
                                          level. As it goes up, the student
                                          gains new abilities in #8bitmooc.
                                          Each new level is unlocked at
                                          100*(2**level) XP.""")
    bio             = models.TextField("Biography",
                                       blank=True,
                                       help_text="""
                                       The student's biographical sketch in
                                       minimarkdown.""")
    public_email    = models.BooleanField("Display E-mail Publicly?",
                                          default=False,
                                          help_text="""
                                          When true, the student's e-mail is
                                          displayed publicly on their profile
                                          page.""")
    ta              = models.BooleanField("Teaching Assistant",
                                          default=False,
                                          help_text="""
                                          When true, the student has access to
                                          grading interfaces.""")
    twitter         = models.SlugField("Twitter",
                                       blank=True,
                                       help_text="""
                                       The student's Twitter handle, withou the
                                       '@' symbol.""")
    blocked_by      = models.ManyToManyField("Student",
                                             verbose_name="Blocked By",
                                             blank=True,
                                             help_text="""
                                             List of students blocking this
                                             student. When this list gets large,
                                             it means the student may be a
                                             problem.""")
    joined   = models.DateTimeField("Joined",
                                   auto_now_add=True,
                                   help_text="""The time the student joined the
                                   MOOC.""")
    last_login  = models.DateTimeField("Last Login",
                                       null=True,
                                       blank=True,
                                       help_text="""The timestamp of the student's
                                       last visit.""")
    this_login  = models.DateTimeField("This Login",
                                       null=True,
                                       blank=True,
                                       help_text="""The timestamp of the student's
                                       most recent login.""")


    # When we represent the student, we put their TA tag on so that others can
    # recognize them.
    def __unicode__(self):
        return u"%s%s (Level %d)" % (self.user.username,
                                     u" [TA]" if self.ta else u"",
                                     self.level)
    
    @property
    def username(self):
        return self.user.username
    
    @property
    def email(self):
        return self.user.email
    
    # Return the percentage of completion to the next level.
    def xp_progress(self):
        return int(self.xp*100. / (100*(2**(self.level))))
    
    # Return number of XP for next level.
    def next_level(self):
        return (100*(2**(self.level)))-self.xp
    
    # Award the student XP. Returns True if the student gains a level.
    def award_xp(self, xp):
        self.xp += xp
        l = LogEntry(student=self,
                     url="XP",
                     notes="+%d XP"%xp)
        l.save()
        self.save()
        if self.next_level() <= 0:
            self.xp = -self.next_level()
            self.level += 1
            l = LogEntry(student=self,
                         url="XP",
                         notes="Level Up!")
            l.save()
            self.save()
            return True
        return False
    
    # Grab the Student out of the request. Returns None if a student is
    # not logged in. If redirect is True, then an error message will be
    # added.
    @staticmethod
    def from_request(request):
        if request.user.is_authenticated():
            try:    return request.user.student
            except: return None
        else: return None


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
                                   help_text="""
                                   Debug information.""")
    
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

