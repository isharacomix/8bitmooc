# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core import exceptions

from nes.models import Pattern
from students.models import Student


# Projects are NES games developed by students in order to learn about the
# NES since the argument for this class is that the only way to learn is to
# find a project you want to work on and learn what you need in order to make
# it work.
class Project(models.Model):
    name        = models.CharField("Project Name",
                                   unique=True,
                                   max_length=200,
                                   help_text="""
                                   Full name of the project.
                                             """)
    slug        = models.SlugField("Shortname",
                                   unique=True,
                                   help_text="""
                                   Slug for the project, used for its URL.
                                             """)
    description = models.TextField("Description",
                                   help_text="""
                                   Description of the project in minimarkdown.
                                             """)
    owner       = models.ForeignKey(Student,
                                    verbose_name="Owner",
                                    related_name="owns",
                                    help_text="""
                                    The original creator of the project.
                                              """)
    team        = models.ManyToManyField(Student,
                                         blank=True,
                                         related_name="works_on",
                                         help_text="""
                                         List of all students who have commit
                                         rights to the project.
                                                   """)
    watched_by  = models.ManyToManyField(Student,
                                         blank=True,
                                         related_name="watches",
                                         help_text="""
                                         List of all students who are following
                                         the project's updates.
                                                   """)
    is_public   = models.BooleanField("Is Public",
                                      default=False,
                                      help_text="""
                                      If True, the project can be found in the
                                      project list by non-team-members.
                                                """)
    code        = models.TextField("Code",
                                   help_text="""
                                   Current source code.
                                             """)
    pattern     = models.ForeignKey(Pattern,
                                    verbose_name="Pattern",
                                    null=True,
                                    blank=True,
                                    help_text="""
                                    The project's sprite sheet.
                                              """)
    forked_from =  models.ForeignKey("Project",
                                    verbose_name="Forked From",
                                    null=True,
                                    blank=True,
                                    help_text="""
                                    Projects can be forked, like on Github. If
                                    this project was forked, this is its parent.
                                              """)
    
    # Representation of the challenge
    def __unicode__(self):
        return u"%s" % (self.name)


# Version history for projects is kept in the form of commits.
class ProjectCommit(models.Model):
    project     =  models.ForeignKey(Project,
                                     verbose_name="Project",
                                     help_text="""
                                     The project of this commit.
                                               """)
    author      = models.ForeignKey(Student,
                                    verbose_name="Author",
                                    help_text="""
                                    Author of the commit.
                                              """)
    timestamp   = models.DateTimeField("Timestamp",
                                       auto_now_add=True,
                                       help_text="""
                                       The time that the URL was accessed.
                                                """)
    diff        = models.TextField("Diff",
                                   help_text="""
                                   Change in source code in a diff format.
                                             """)
    comment     = models.TextField("Comment",
                                   help_text="""
                                   Comment about the commit.
                                             """)

    # Representation of the commit
    def __unicode__(self):
        return u"Commit %d for %s" % (self.id, self.project.name)


# Students can leave comments on projects.
class ProjectComment(models.Model):
    author      = models.ForeignKey(Student,
                                    verbose_name="Author",
                                    help_text="""
                                    Author of the comment.
                                              """)
    timestamp   = models.DateTimeField("Timestamp",
                                       auto_now_add=True,
                                       help_text="""
                                       The time that the URL was accessed.
                                                """)
    content     = models.TextField("Content",
                                   help_text="""
                                   Comment in minimarkdown.
                                             """)
    is_public   = models.BooleanField("Is Public",
                                      default=True,
                                      help_text="""
                                      If True, the comment can be seen by
                                      non-team members.
                                                """)
    
    # Representation of the challenge
    def __unicode__(self):
        return u"Comment %d on %s" % (self.id, self.project.name)


