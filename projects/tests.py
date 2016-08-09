"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from projects.models import Project
from projects.models import Client
from projects.models import Project_Manager
from projects.models import UserProfile
from django.contrib.auth.models import User


class ProjectTest(TestCase):
    def setup(self):
        t = Client.objects.create(name='abc')
        users= User.objects.create(username='first_name',password='123')
        userprofiles = UserProfile.objects.create(user=users,first_name='av',last_name='bv',access_level='Administrator')
        v = Project_Manager.objects.create(name='abcd',userprofile=userprofiles)
    
    def test_project(self):
        t = Client.objects.create(name='abc')
        users= User.objects.create(username='first_name',password='123')
        userprofiles = UserProfile.objects.create(user=users,first_name='av',last_name='bv',access_level='Administrator')
        v = Project_Manager.objects.create(name='abcd',userprofile=userprofiles)
        self.assertEqual(v.name, 'abcd')
