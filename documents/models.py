from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import gettext as _
from projects.models import Project
from tasks.models import *
from milestones.models import *

class Document(models.Model):

    person = models.ForeignKey(UserProfile, blank = False, null=False, related_name='Uploaded by')
    title = models.CharField(max_length=100)
    files = models.FileField(upload_to='static/documents/%Y/%m/%d')
    project = models.ForeignKey(Project)
    tags = models.CharField(max_length=100)
    notes = models.TextField(blank=True,null=True)
    #content_type = models.ForeignKey(ContentType)
    tasks  = models.ForeignKey(Tasks, blank=True, null=True)
    milestone = models.ForeignKey(Milestone, blank=True, null=True)
    #objects_id = models.PositiveIntegerField()
    optional_information = models.NullBooleanField()
    active = models.IntegerField(default=2)

    def __unicode__(self):
        return self.title

