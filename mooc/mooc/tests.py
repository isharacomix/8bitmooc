# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from students.models import Student, LogEntry


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

