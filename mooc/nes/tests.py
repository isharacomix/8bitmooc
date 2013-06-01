# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from students.models import Student
from nes.assembler import Assembler
from nes.emulator import Emulator
from nes.models import Pattern, Game

# This test class tests the NES's various functionalities. Ideally this
# will become a full test suite for assemblers and emulators.
class TestAssembler(TestCase):
    def setUp(self):
        self.A = Assembler()
        self.E = Emulator()
    
    # 
    def sanity(self):
        self.assertTrue(True)


class TestNESViews(TestCase):
    def setUp(self):
        self.c = Client()
        self.u1 = User.objects.create_user("ishara",
                                           "ishara@isharacomix.org",
                                           "ishararulz")
        self.u1.save()
        self.s1 = Student( user=self.u1, twitter="isharacomix" )
        self.s1.save()
    
        # Give the test users memorable names.
        self.ishara = self.s1
        
        self.G = Game(title="Foo", code="")
        self.G.save()
        self.G.authors.add(self.ishara)

    #
    def test_arcade(self):
        response = self.c.get("/play/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("http://twitter.com/isharacomix" in response.content)
        response = self.c.get("/play/1/?download", follow=True)
        self.assertEqual(response.status_code, 200)

