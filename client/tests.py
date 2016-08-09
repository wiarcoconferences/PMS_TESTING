"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from client.models import Client


class ClientTest(TestCase):
    def setup(self):
        t = Client.objects.create(name="abc", status=0, address='abc', 
        email='acb@a.com', website='http://.google.com', 
        phone=01234656, fax=0123456, description='abcclient')
        self.assertEqual(t.name, 'abc')


    def test_client(self):
        t = Client.objects.create(name="abc", status=0, address='abc', 
        email='acb@a.com', website='http://www.google.com', phone=01234656, 
        fax=0123456, description='abcclient')
        self.assertEqual(t.name, 'abc')
