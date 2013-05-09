# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client

from django.contrib.auth.models import User
from wiki.models import Page
from students.models import Student
from world.models import World, Stage, Achievement, QuizChallenge


# This class tests the World and Lesson system. Here is the test data.
# World 1-1 is open, and is a prereq to 1-2 and 1-3 (which is hidden).
# Ishara has not completed any levels.
# Alexis has completed 1-1.
# TODO verify that getting achievements unlocks new worlds.
class LessonTests(TestCase):
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

        # Let's create a world with three stages.
        self.W = World( name = "Fun World",
                        shortname = "1",
                        description = "The best world ever." )
        self.W.save()
        self.Q = QuizChallenge( content = "foo",
                                score = 10 )
        self.Q.save()
        self.l1 = Stage( name = "Fun Level 1",
                         shortname = "1",
                         lesson = self.t2,
                         challenge = self.Q,
                         world = self.W,
                         graphic = "foo")
        self.l2 = Stage( name = "Fun Level 2",
                         shortname = "2",
                         lesson = self.t2,
                         world = self.W)
        self.l3 = Stage( name = "Fun Level 3",
                         shortname = "3",
                         challenge = self.Q,
                         world = self.W,
                         hidden = True)
        self.l1.save()
        self.l2.save()
        self.l3.save()
        self.l2.prereqs1.add(self.l1)
        self.l3.prereqs1.add(self.l1)
        self.l2.save()
        self.l3.save()
        
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
        
        # Give the test users memorable names.
        self.ishara = self.s1
        self.alexis = self.s2
        
        self.l1.completed_by.add(self.alexis)
        self.l1.save()
       
    # Anonymous viewers can not access the pages - they will be redirected
    # to the log-in/sign-up page. 
    def test_anon_lessons(self):
        pass
    
    # When a user visits a stage that doesn't have a lesson, they go directly
    # to the challenge.
    def test_go_challenge(self):
        self.c.login(username="alexis", password="alexisrulz")
        response = self.c.get("/world/1/3/", follow=True)
        self.assertEqual(response.redirect_chain, [(u'http://testserver/world/1/3/challenge/', 302)])
        response = self.c.get("/world/1/3/lesson/", follow=True)
        self.assertEqual(response.redirect_chain, [(u'http://testserver/world/1/3/challenge/', 302)])
        
    # When a user visits a stage that doesn't have a challenge, they go directly
    # to the lesson.
    def test_go_challenge(self):
        self.c.login(username="alexis", password="alexisrulz")
        response = self.c.get("/world/1/2/", follow=True)
        self.assertEqual(response.redirect_chain, [(u'http://testserver/world/1/2/lesson/', 302)])
        response = self.c.get("/world/1/2/challenge/", follow=True)
        self.assertEqual(response.redirect_chain, [(u'http://testserver/world/1/2/lesson/', 302)])
    
    # Test the world map. Ishara will see two stages, while Alexis will see 3.
    def test_world_map(self):
        self.c.login(username="alexis", password="alexisrulz")
        response = self.c.get("/world/1/")
        self.assertTrue( "Fun Level 3" in response.content )
        self.c.logout()
        self.c.login(username="ishara", password="ishararulz")
        response = self.c.get("/world/1/")
        self.assertFalse( "Fun Level 3" in response.content )
        self.assertTrue("The best world ever" in response.content )
    
    
    # TODO test the quizzes and stuff

