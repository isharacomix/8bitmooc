# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

from students.models import Student
from world.models import World


# A chat message.
class Chat(models.Model):
    content     = models.CharField("content", max_length=140,
                        help_text="Content of the chat.")
    timestamp = models.DateTimeField("timestamp", auto_now=True)
    author      = models.ForeignKey(Student, verbose_name="author")
    channel     = models.ForeignKey(World, verbose_name="channel")
    
    # You can set up your chat feed to ignore messages your friends have
    # dismissed or even only see posts your friends have endorsed. This
    # makes it possible to curate the firehose.
    endorsed_by = models.ManyToManyField(Student, blank=True,
                  related_name='endorsed+')
    dismissed_by = models.ManyToManyField(Student, blank=True,
                   related_name='dismissed+')
    
    class Meta:
            ordering = ('timestamp',)

    # Unicode representation.
    def __unicode__(self):
        return u"%s" % (self.name)


