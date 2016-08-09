from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from projects.models import Project
from people.models import UserProfile
from client.models import Client, Base
from django.db import IntegrityError

# Create your models here.

STATUS = (('In Progress', 'In Progress'),('Complete', 'Complete'))

class Milestone(Base):
    title = models.TextField(max_length=100)
    client = models.ForeignKey('client.Client', blank=True, null=True, related_name='related_to_client')
    project = models.ForeignKey(Project)
    owned_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='related_to_owned_by')
    description = models.TextField(max_length=100, blank=True, null=True)
    due_date = models.DateField('Due Date', blank=True, null=True)
    #status = models.CharField(max_length=30,choices=STATUS, blank=True, null=True)
    status = models.BooleanField()
    available_task = models.ManyToManyField('tasks.Tasks', blank=True, null=True, related_name='related_to_advanced_milestone')
    activate = models.IntegerField(blank=True, null=True, default=2)

    def __unicode__(self):
        return self.title

    def get_task_actual_time(self):
        from tasks.models import Tasks
        actual_time = Tasks.objects.filter(milestone=self)
        return actual_time

    def get_task_actual(self):
        from tasks.models import Tasks
        actual = Tasks.objects.filter(milestone=self)
        return actual

    def get_userprofile(self):
        userprofile_list = UserProfile.objects.filter(milestone=self)
        return userprofile_list

    def get_tasks_list(self):
        task_list = Tasks.objects.filter(milestone=self)
        return task_list

    class Meta:
        ordering = ('title', )



class Milestone_Document(models.Model):
    milestone_documents = models.ForeignKey('milestones.Milestone', blank=True, null=True, related_name='related_to_milestone')
    files = models.FileField(upload_to='static/milestone_documents', blank=True, null=True)
    title = models.CharField(max_length=100)
    tags = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.title

