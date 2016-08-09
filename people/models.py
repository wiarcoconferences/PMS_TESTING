from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from client.models import *
from mastermodule.models import *
import datetime


Access_Level_CHOICES = (('1', 'Administrator'), ('2','Project Manager'), ('3','Resource'), ('4','Executive'))
add_Choices = (('1', 'Work'), ('2', 'Home'), ('3', 'Other'))
Phone = (('1', 'Fax'), ('2', 'Home'), ('3', 'Mobile'), ('4', 'Skype'), ('4', 'Work'), ('5', 'Others'))
Network_Types = (('1', 'AIM'), ('2', 'Facebook'), ('3', 'Google Talk'), ('4', 'ICQ'), ('5', 'IRC'), ('6', 'Jabber'), ('7', 'MySpaceIM'), ('8', 'Skype'), ('9', 'Twitter'), ('10', 'Windows Live MSN'), ('11', 'Yahoo!'), ('12', 'Other'))
Designation_CHOICES = (('1', 'Designer'), ('2', 'Senior Programmer'), ('3', 'Junior Programmer'), ('4', 'System Administrator'))
Title_choices = (('Mr.', 'Mr.'), ('Ms.', 'Ms.'), ('Mrs.', 'Mrs.'))


from projects.models import *
class UserProfile(Base):
    user = models.ForeignKey(User)
    active = models.IntegerField(blank=True, null=True, default=2)
    client = models.ForeignKey(Client, blank=True, null=True, related_name="client_related_to_userprofile")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True, null=True, choices=Title_choices)
    address = models.TextField(blank=True, null=True)
    address_choices = models.CharField(max_length=20, blank=True, null=True, choices=add_Choices)
    email = models.EmailField(blank=True, null=True)
    email_choices= models.CharField(max_length=20, choices = add_Choices, blank=True, null=True)
    phone = models.CharField(max_length=12, blank=True, null=True)
    phone_choices = models.CharField(max_length=20, choices=Phone, blank=True, null=True)
    network = models.CharField(max_length =20, blank=True, null=True)
    network_types = models.CharField(max_length=20, choices=Network_Types, blank=True, null=True)
    website = models.URLField(max_length=100, blank=True)
    notes = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='static/img', blank=True, null=True)
    access_level = models.CharField(max_length=40, choices = Access_Level_CHOICES)
    resource_categorization = models.ForeignKey(Resource_Categorization, blank=True, null=True)
    now = datetime.datetime.now()
    uuid = models.CharField(max_length=100, blank=True, null=True)
    project = models.ManyToManyField('projects.Project', blank=True, null=True, related_name='project_permission')
    resource_categorization = models.ForeignKey(Resource_Categorization, blank=True, null=True)
    
    
    def __unicode__(self):
        return self.first_name
    
    def get_project_permission(self):
        projects = UserProfile.objects.filter(project=self)
        return projects

    def get_milestones_list(self):
        from milestones.models import Milestone
        milestones = Milestone.objects.filter(owned_by=self)
        return milestones

    def get_tasks_list(self):
        from tasks.models import Tasks
        tasks = UserProfile.objects.filter(owned_by=self)
        return tasks

    def get_person(self):
        from times.models import AddTime
        person = UserProfile.objects.filter(person=self)
        return get_person


