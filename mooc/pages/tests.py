# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from pages.models import Page


# This will test the the sanity of the markup language.
class TestAssembler(TestCase):
    def setUp(self):
        pass
    
    # 
    def sanity(self):
        self.assertTrue(True)

