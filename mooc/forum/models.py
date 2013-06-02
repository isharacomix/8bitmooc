# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core import exceptions

from students.models import Student

# Discussion boards are the highest level of abstraction in the forums.
# Discussion boards can only be created by TAs.
class DiscussionBoard(models.Model):
    name        = models.CharField("Board Name",
                                   unique=True,
                                   max_length=200,
                                   help_text="""Full name of the discussion
                                   board.""")
    slug        = models.SlugField("Shortname",
                                   unique=True,
                                   help_text="""Slug for the discussion board,
                                   used for its URL.""")
    description = models.TextField("Description",
                                   help_text="""Description of the board in
                                   minimarkdown.""")
    restricted  = models.IntegerField("Restriction",
                                      help_text="""Minimum level needed to
                                      access the board. Set to a high value
                                      for a TA board.""")
    wrestricted = models.IntegerField("Write Restriction",
                                      help_text="""Minimum level needed to
                                      post to the board. Set to a high value
                                      for a TA board.""")
    
    # Order by restriction levels.
    class Meta:
        ordering = ['restricted','-wrestricted']
    
    # Representation of the challenge
    def __unicode__(self):
        return u"%s Discussion Board" % (self.name)


# A topic within a discussion board. Can be created by any student in good
# standing
class DiscussionTopic(models.Model):
    title        = models.CharField("Topic Title",
                                    max_length=200,
                                    help_text="""Full name of the discussion
                                    board.""")
    author      = models.ForeignKey(Student,
                                    verbose_name="Author",
                                    help_text="""Author of the comment.""")
    board       = models.ForeignKey(DiscussionBoard,
                                    verbose_name="Discussion Board",
                                    help_text="""The board on which the topic
                                    resides.""")
    sticky      = models.BooleanField("Sticky",
                                      default=False,
                                      help_text="""Sticky topics appear on the
                                      first page of the board.""")
    locked      = models.BooleanField("Locked",
                                      default=False,
                                      help_text="""Locked posts can't be replied
                                      to.""")
    hidden      = models.BooleanField("Hidden",
                                      default=False,
                                      help_text="""Hidden topics can never be
                                      seen again.""")
    last_active = models.DateTimeField("Last Active",
                                       auto_now=True,
                                       help_text="""The last time this topic
                                       was modified.""")

    # Order these by difficulty.
    class Meta:
        ordering = ['-sticky','-last_active']

    # Representation of the commit
    def __unicode__(self):
        return u"Discussion: %s" % (self.title)


# Replies to forum topics.
class DiscussionPost(models.Model):
    author      = models.ForeignKey(Student,
                                    verbose_name="Author",
                                    help_text="""Author of the post.""")
    timestamp   = models.DateTimeField("Timestamp",
                                       auto_now_add=True,
                                       help_text="""The time that the post was
                                       written.""")
    content     = models.TextField("Content",
                                   help_text="""Post in minimarkdown.""")
    topic       = models.ForeignKey(DiscussionTopic,
                                    verbose_name="Topic",
                                    help_text="""Topic containing this post.""")
    upvotes     = models.IntegerField("Upvotes",
                                      default=0,
                                      help_text="""Upvotes by other students.""")
    downvotes   = models.IntegerField("Downvotes",
                                      default=0,
                                      help_text="""Downvotes by other students.""")
    hidden      = models.BooleanField("Hidden",
                                      default=False,
                                      help_text="""Hidden posts can never be
                                      seen again.""")
             
    # Order these by difficulty.
    class Meta:
        ordering = ['timestamp']
    
    # Representation of the challenge
    def __unicode__(self):
        return u"Post %d on %s" % (self.id, self.topic.title)


