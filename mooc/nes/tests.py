# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from students.models import Student
from nes.assembler import Assembler
from nes.emulator import Emulator

# This test class tests the NES's various functionalities. Ideally this
# will become a full test suite for assemblers and emulators.
class TestAssembler(TestCase):
    def setUp(self):
        self.A = Assembler()
        self.E = Emulator()
    
    # 
    def sanity(self):
        self.assertTrue(True)

