# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from pages.models import Page


# This will test the the sanity of the markup language.
class TestAssembler(TestCase):
    def setUp(self):
        self.c = Client()
        
        p = Page(name="index", content="Hello world")
        p.save()
        p = Page(name="test", content="This is a test.")
        p.save()
    
    # Test to make sure we can visit pages that exist.
    def test_pages(self):
        response = self.c.get("/help/index/")
        self.assertEqual( response.status_code, 200 )
        response = self.c.get("/help/test/")
        self.assertEqual( response.status_code, 200 )
        response = self.c.get("/help/nope/")
        self.assertEqual( response.status_code, 404 )

    # Make sure searching works.
    def test_search(self):
        response = self.c.get("/help/index/?search=test", follow=True)
        self.assertEqual( response.redirect_chain[-1][0], "http://testserver/help/test/")
        response = self.c.get("/help/index/?search=world", follow=True)
        self.assertTrue( "/help/index/" in response.content )
        
        
