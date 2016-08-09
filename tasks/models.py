from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from projects.models import Project
from milestones.models import Milestone
from client.models import Client
from client.models import Base
from people.models import UserProfile
from mastermodule.models import Task_Statuses
from mastermodule.models import Task_priorities
from mastermodule.models import Modules
from django.db import IntegrityError
from django.utils.translation import gettext as _

MODULE = (('Design', 'Design'), ('Development', 'Development'), ('Discovery', 'Discovery'), ('Out of Scope', 
        'Out of Scope'), ('Production', 'Production'), ('Quality Assurance', 'Quality Assurance'))


STATUS = (('Open', 'Open'), ('Need', 'Need'), ('Assistance', 'Assistance'), ('Verify & Close', 'Verify & Close'), ('Reassign', 'Reassign'),
        ('Client Review', 'Client Review'), ('Closed', 'Closed'))

PRIORITY = (('Major', 'Major'), ('Showstopper', 'Showstopper'), ('Medium', 'Medium'), ('Low', 'Low'))


class Tasks(Base):
    title = models.TextField(max_length=100)
    client = models.ForeignKey(Client, blank=True, null=True)
    project = models.ForeignKey(Project)
    module = models.ForeignKey(Modules)
    start_date = models.DateField('Start Date')
    due_date = models.DateField('Due Date',blank=True, null=True)
    milestone = models.ForeignKey(Milestone, blank=True, null=True)
    status = models.ForeignKey(Task_Statuses)
    priority = models.ForeignKey(Task_priorities)
    owned_by = models.ManyToManyField(UserProfile, related_name='owned_by')
    assigned_to = models.ManyToManyField(UserProfile,related_name='assigned_by', blank=True, null=True)
    followed_by = models.ManyToManyField(UserProfile, related_name='followed_by', blank=True,null=True)
    estimated = models.FloatField(blank=True, null=True, default=None)
    actual = models.FloatField(blank=True, null=True, default=None)
    summary = models.TextField(max_length=100, blank=True, null=True)
    bug_reports = models.FileField(upload_to='static/bug reports', blank=True, null=True)

    def __unicode__(self):
        return self.title

    def get_total_actual(self):
        actual = 0
        same_date_list =  Tasks.objects.filter(start_date=self.start_date)
        for i in same_date_list:
            actual = float(actual)+float(i.actual)
        return actual

    def get_projects_list(self):
        projects = Project.objects.filter(project=self)
        return projects


    class Meta:
        ordering = ('title', )



class Request(models.Model):
    title = models.TextField(max_length=100)
    client = models.ForeignKey(Client)
    project = models.ForeignKey(Project)
    frm = models.ForeignKey(UserProfile, related_name='frm')
    priority = models.ForeignKey(Task_priorities)
    requested_due_date = models.DateField('Requested Due Date')
    description = models.TextField(max_length=100, blank=True, null=True)
    doc = models.FileField(upload_to='static/rdocuments', blank=True, null=True)


    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('title', )




