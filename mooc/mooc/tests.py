from django.test import TestCase
from django.test.client import Client


# This class tests the MOOC's basic functionality
class MoocTests(TestCase):
    def setUp(self):
        self.c = Client()
       
    # Try to go to the home page.
    def test_can_read_textbook(self):
        response = self.c.get("/")
        self.assertEqual(response.status_code, 200)

