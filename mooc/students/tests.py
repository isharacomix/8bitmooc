# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from students.models import Student, LogEntry


# Test user logging in and registration.
class TestLoggingIn(TestCase):
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
    
    # Test User Connection decorators.
    def test_user_fields(self):
        self.assertEquals(self.s1.username, self.u1.username)
        self.assertEquals(self.s1.email, self.u1.email)
    
    # First, just make sure we can visit all of the pages successfully.
    def test_visit_pages(self):
        response = self.c.get("/sign-in/")
        self.assertEqual(response.status_code, 200)
        response = self.c.get("/sign-out/", follow=True)
        self.assertEqual( response.redirect_chain[-1][0], "http://testserver/sign-in/")
        
    # Try to log in using a post request.
    def test_log_in(self):
        response = self.c.post('/sign-in/',
                               {'username': 'ishara', 'password': 'ishararulz'},
                               follow=True)
        self.assertEqual( response.redirect_chain[-1][0], "http://testserver/")
        self.assertTrue("Hello, ishara!" in response.content)

    # Try failing logging in. We should get no 404's.
    def test_failed_log_in(self):
        response = self.c.post('/sign-in/',
                               {'username': 'ishara'},
                               follow=True)
        self.assertEqual( response.redirect_chain[-1][0], "http://testserver/sign-in/")
        self.assertTrue("Hello, ishara!" not in response.content)

        response = self.c.post('/sign-in/',
                               {'username': 'ishara', 'password': 'ramenrulz'},
                               follow=True)
        self.assertEqual( response.redirect_chain[-1][0], "http://testserver/sign-in/")
        self.assertTrue("Incorrect username or password" in ' '.join(response.content.split()))
        self.assertTrue("Hello, ishara!" not in response.content)

    # Try testing a not-verified user.
    def test_unverified(self):
        self.u2 = User.objects.create_user("alexis",
                                           "alexis@isharacomix.org",
                                           "alexisrulz")
        self.u2.save()
        response = self.c.post('/sign-in/',
                               {'username': 'alexis', 'password': 'alexisrulz'},
                               follow=True)
        self.assertEqual( response.redirect_chain[-1][0], "http://testserver/sign-in/")
        self.assertTrue("Please check your e-mail" in ' '.join(response.content.split()))
        self.assertTrue("Hello, alexis!" not in response.content)        

