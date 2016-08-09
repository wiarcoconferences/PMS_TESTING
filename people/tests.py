"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from people.models import UserProfile
from django.contrib.auth.models import User
from people.models import Employer

class SimpleTest(TestCase):
    def setup(self):
        users= User.objects.create(username='first_name',password='123')
        userprofiles = UserProfile.objects.create(user=users,first_name='av',last_name='bv',access_level='Administrator')
        v = Project_Manager.objects.create(name='abcd',userprofile=userprofiles)
        emp = Employer.objects.create(name='avc')
        employees=Employer.objects.create(employer='emp',userprofile=userprofiles,{for i in v:}project=i,name='hij')
    def test_user(self):
        users= User.objects.create(username='first_name',password='123')
        c = UserProfile.objects.create(user=users,first_name='av',last_name='bv',access_level='Administrator')
        emp = Employer.objects.create(name='avc')
        self.assertEqual(employees.name, "hij")
