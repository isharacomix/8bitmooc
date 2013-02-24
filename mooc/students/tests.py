from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from students.models import Student


# This class tests the Student functionality, including the User Profile
# connection, the personal profile pages, etc.
class StudentTests(TestCase):
    def setUp(self):
        self.c = Client()
        self.u1 = User.objects.create_user("ishara",
                                           "ishara@isharacomix.org",
                                           "ishararulz")
        self.s1 = Student( user=self.u1 )
        self.s1.save()
    
        # Give the test users memorable names.
        self.ishara = self.s1
    
    # Test User Connection decorators.
    def test_user_fields(self):
        self.assertEquals(self.s1.username, self.u1.username)
        self.assertEquals(self.s1.email, self.u1.email)

