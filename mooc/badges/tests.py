"""
Tests for the badges.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from badges.models import Badge
from students.models import Student

class BadgeModelTest(TestCase):
    def test_held_by(self):
        """
        This tests the 'held_by' function of the badge model, despite it
        being against the design philosophy for the badge to store who it
        is awarded to rather than the user asserting the badge for themself.
        """
        
        # Create the test badge.
        b = Badge( name = "superbadge",
                   shortname = "superbadge",
                   description = "superbadge",
                   graphic = "superbadge" )
        b.save()
        
        # Create some test users.
        u1 = User( username="kellydoctor", email="kelly@doctor.com" )
        u1.save()
        s1 = Student( user=u1 )
        s1.save()
        u2 = User( username="andyprogrammer", email="andy@programmer.com" )
        u2.save()
        s2 = Student( user=u2 )
        s2.save()
        
        # Award the badge to s1
        b.awarded_to.add( s1 )
        b.save()
        
        # Now run the tests.
        self.assertTrue( b.held_by( s1 ) )
        self.assertFalse( b.held_by( s2 ) )
        
