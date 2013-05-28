# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from students.models import Student, LogEntry
from pages.models import Page


# This class tests the MOOC's basic functionality
class TestMooc(TestCase):
    def setUp(self):
        self.c = Client()
        
        self.u1 = User.objects.create_user("ishara",
                                           "ishara@isharacomix.org",
                                           "ishararulz")
        self.u1.save()
        self.s1 = Student( user=self.u1 )
        self.s1.save()
        
        
        p = Page(name="index", content="Hello world")
        p.save()
        p = Page(name="test", content="This is a test.")
        p.save()
    
        # Give the test users memorable names.
        self.ishara = self.s1
       
    # Try to go to the home page.
    def test_home_page(self):
        response = self.c.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("/sign-up/" in response.content)
    
    # Log in and go to the home page.
    def test_logged_in_dash(self):
        self.c.login(username="ishara", password="ishararulz")
        response = self.c.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("/sign-out/" in response.content)

    # Make sure searching works.
    def test_search(self):
        response = self.c.get("/search/?query=world", follow=True)
        self.assertTrue( "/help/index/" in response.content )
        

