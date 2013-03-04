# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

from students.models import Student
from lessons.models import World


# A chat message.
class Chat(models.Model):
    content     = models.CharField("content", max_length=140,
                        help_text="Content of the chat.")
    timestamp = models.DateTimeField("timestamp", auto_now=True)
    author      = models.ForeignKey(Student, verbose_name="author", null=True)
    channel     = models.ForeignKey(World, verbose_name="channel", null=True)
    
    class Meta:
            ordering = ('timestamp',)

    # Unicode representation.
    def __unicode__(self):
        return u"%s" % (self.name)


