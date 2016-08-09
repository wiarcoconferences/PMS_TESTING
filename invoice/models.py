from django.db import models
from projects.models import *



class Invoices(models.Model):
    project = models.ForeignKey(Project)
    title = models.CharField(max_length=100)
    terms = models.CharField(max_length=40)
    
    def __unicode__(self):
        return self.title
        
