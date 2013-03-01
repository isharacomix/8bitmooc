# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from textbook.models import Page


# This class tests the Textbook, including the Creole markup.
class TextBookTests(TestCase):
    def setUp(self):
        self.c = Client()
        self.t1 = Page( title="index",
                        content="sup" )
        self.t2 = Page( title="epic",
                        content="""
                        = This is a truly epic tale.
                        == OMG
                        === fur reals
                          
                        It stars **Ishara** //Alexis// and __Allen__.
                         
                        --THE END--
                        """)
        self.t1.save()
        self.t2.save()
       
    # Check the wiki page rendering. 
    def test_can_read_textbook(self):
        response = self.c.get("/textbook/epic/")
        self.assertEqual(response.status_code, 200)

    # When a non-existant page is loaded, a 404 error is returned.
    def test_404(self):
        response = self.c.get("/textbook/fake/")
        self.assertEqual(response.status_code, 404)
    
    # When you don't specify a page, we redirect to the index.
    def test_redirect_index(self):
        response = self.c.get("/textbook/", follow=True)
        self.assertEqual(response.redirect_chain, [(u'http://testserver/textbook/index/', 302)])
        

