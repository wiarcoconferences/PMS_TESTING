from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from django.contrib.contenttypes import generic
from people.models import *
from client.models import Client
from mastermodule.models import Work_Type

PROJECT_STATUS_TYPES = (('Maintenance','Mainteanace'),('Ongoing','Ongoing'),('Complete','Complete'))

class Project_Manager(models.Model):
    name = models.CharField(max_length=100,blank=True,null=True)
    from people.models import UserProfile
    userprofile = models.ForeignKey(UserProfile)

    def __unicode__(self):
        return self.userprofile.user.first_name

class Project(Base):
    client = models.ForeignKey(Client,blank=True,null=True)
    name = models.CharField(max_length=100)
    project_manager = models.ForeignKey(Project_Manager,blank=True,null=True)
    active = models.IntegerField(default=2)
    project_status = models.CharField(max_length=20,choices =PROJECT_STATUS_TYPES,blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    billable = models.PositiveIntegerField(blank=True, null=True, default=2)
    start_date = models.DateField(blank = True, null = True)
    end_date = models.DateField(blank = True, null = True)
    budget = models.FloatField(default = None,blank=True,null=True)
    alert = models.FloatField(default = None,blank=True,null=True)
    
    def __unicode__(self):
        return self.name
    
    def get_user_profile(self):
        from projects.models import UserProfile
        people = UserProfile.objects.filter(project__id=self.id)
        return people
    def get_managers(self):
        managers = []
        for profile in self.get_user_profile():
            if profile.access_level == "Project Manager":
                managers.append(profile)
        return managers
    def get_users(self):
        from projects.models import UserProfile
        people = UserProfile.objects.get(project=self)
        return people
        
    def get_peoples(self):
        from projects.models import UserProfile
        person = [person 
                    for person in UserProfile.objects.all()
                        if self in person.project.all()]
        return person
        
    def get_tasks_list(self):
        from tasks.models import Tasks
        task = Tasks.objects.filter(project=self)
        return task
        
    def get_milestones_list(self):
        from milestones.models import Milestone
        milestones = Milestone.objects.filter(project=self)
        return milestones
        
    def get_clients_list(self):
        clients_list = Client.objects.filter(project=self)
        return clients_list
        
    def get_modules(self):
        return Modules.objects.filter(content_type__name__iexact="project",object_id=self.id)
        
    def get_unclosed_task_list(self):
        from tasks.models import Tasks
        return Tasks.objects.filter(project=self).exclude(status__name='Closed')
        
    def get_no_assignee_task_list(self):
        from tasks.models import Tasks
        return Tasks.objects.filter(project=self,assigned_to=None)
        
class Project_Module_Relationship(Base):
    global_module = models.IntegerField(default=2)
    project = models.ForeignKey(Project,blank=True,null=True)
    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_('content type'),
                                     related_name='Content_Type_Of_Modules')
    object_id = models.TextField(_('object ID'))
    
    
    def __unicode__(self):
        return self.project.name
