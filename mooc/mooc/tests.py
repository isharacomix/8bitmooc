# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

# This class tests the MOOC's basic functionality
class TestMooc(TestCase):
    def setUp(self):
        self.c = Client()
       
    # Try to go to the home page.
    def test_home_page(self):
        response = self.c.get("/")
        self.assertEqual(response.status_code, 200)

