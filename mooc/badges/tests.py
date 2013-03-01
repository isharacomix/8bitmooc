# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from badges.models import Badge
from students.models import Student


# This class tests most of the badge functionality.
# Test Data:
#   One Badge (the super badge)
#   Two Students (Ishara and Alexis)
#   Alexis has the super badge
class BadgeTests(TestCase):
    def setUp(self):
        self.c = Client()
        
        # Create the test badge.
        self.b = Badge( name = "The Super Badge",
                        shortname = "superbadge",
                        description = "This badge is quite super.",
                        graphic = "superbadge" )
        self.b.save()
        
        # Create some test users.
        self.u1 = User.objects.create_user("ishara",
                                           "ishara@isharacomix.org",
                                           "ishararulz")
        self.u2 = User.objects.create_user("alexis",
                                           "alexis@isharacomix.org",
                                           "alexisrulz")
        self.s1 = Student( user=self.u1 )
        self.s2 = Student( user=self.u2 )
        self.s1.save()
        self.s2.save()
        
        # Award the badge to s1
        self.b.awarded_to.add( self.s2 )
        self.b.save()
        
        # Give the test users memorable names.
        self.ishara = self.s1
        self.alexis = self.s2
    
    # Test the model's "held_by" method.
    def test_held_by(self):
        self.assertFalse( self.b.held_by( self.ishara ) )
        self.assertTrue( self.b.held_by( self.alexis ) )
    
    # When an anonymous user visits the badge list (/badges/) they see the
    # superbadge.
    def test_view_badge_list(self):
        response = self.c.get('/badges/')
        self.assertEqual(response.status_code, 200)
        response = self.c.get('/badges/superbadge/')
        self.assertEqual(response.status_code, 200)
    
    # When you go to a badge that doesn't exist, you get redirected back to
    # '/badges'.
    def test_badge_redirect(self):
        response = self.c.get('/badges/fakebadge/', follow=True)
        self.assertEqual(response.redirect_chain, [(u'http://testserver/badges/', 302)])

    # When Alexis visits the badge list, she sees a check mark next to
    # the superbadge.
    def test_view_badge_list_check(self):
        self.c.login(username="alexis", password="alexisrulz")
        response = self.c.get('/badges/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue( '<i class="icon-ok"></i>' in response.content )

    # When Ishara visits the badge list, he doesn't see a check mark next to
    # the superbadge.
    def test_view_badge_list_nocheck(self):
        self.c.login(username="ishara", password="ishararulz")
        response = self.c.get('/badges/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse( '<i class="icon-ok"></i>' in response.content )
    
    # When Alexis visits the badge information, she can add the badge to her
    # backpack.
    def test_badge_backpack_button(self):
        self.c.login(username="alexis", password="alexisrulz")
        response = self.c.get('/badges/superbadge/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue( 'http://beta.openbadges.org/issuer.js' in response.content )

    # When Ishara visits the badge information, he can not add the badge to his
    # backpack.
    def test_view_badge_list_nocheck(self):
        self.c.login(username="ishara", password="ishararulz")
        response = self.c.get('/badges/superbadge/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse( 'http://beta.openbadges.org/issuer.js' in response.content )    
    
    # Check to ensure that you get a 404 for the assertion for Ishara and a
    # JSON string for Alexis.
    def test_badge_assertion(self):
        response = self.c.get('/badges/superbadge/ishara/')
        self.assertEqual(response.status_code, 404)
        response = self.c.get('/badges/superbadge/ramen/')
        self.assertEqual(response.status_code, 404)
        response = self.c.get('/badges/superbadge/alexis/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

