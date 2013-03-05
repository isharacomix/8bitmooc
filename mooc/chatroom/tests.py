# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from students.models import Student
from lessons.models import World
from chatroom.models import Chat


# Test the chatting functionality, yo.
class ChatTests(TestCase):
    def setUp(self):
        self.c = Client()
        self.u1 = User.objects.create_user("ishara",
                                           "ishara@isharacomix.org",
                                           "ishararulz")
        self.s1 = Student( user=self.u1 )
        self.s1.save()
        
        self.ishara = self.s1
        
        self.W = World()
        self.W.name = "Test World"
        self.W.shortname = "test"
        self.W.save()

    # This tests the chatting. Until we actually finalize the chatroom spec,
    # this is as much as I care to do.
    def test_chatting(self):
        self.c.login(username="ishara", password="ishararulz")
        response = self.c.post('/chat/', {"function":"send",
                                          "channel":"test",
                                          "message":"Hello world!"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        l = Chat.objects.all()
        self.assertEqual(len(l),1)
        
