from django.db import models
from client.models import *
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType

TERM_CHOICES = (('None', 'None'), ('Upon Receipt', 'Upon Receipt'), ('Next 15', 
'Next 15'), ('Next 30', 'Next30') )


INTERVAL_DOMAIN = (('Select one...', 'Select one...'), ('intervalsonline.com', \
'intervalsonline.com'), ('projectaccount.com' ,'projectaccount.com'))

DEFAULT_TIME = (('Select one...','Select one...'), \
('1/10 of an hour (6 minutes)','1/10 of an hour (6 minutes)'), \
('1/8 of an hour (7.5 minutes)','1/8 of an hour (7.5 minutes)'), \
('1/4 of an hour (15 minutes)','1/4 of an hour (15 minutes)'), \
('1/2 of an hour (30 minutes)','1/2 of an hour (30 minutes)'))

class Generalinfo(models.Model):
    Company_Name = models.CharField(max_length=40)
    Intervals_Domain_Name = models.CharField(max_length=40)
    Intervals_Domain = models.CharField(max_length=40,choices=INTERVAL_DOMAIN)
    Intervals_Admin = models.CharField(max_length=40)
    Default_time = models.CharField(max_length=40,choices=DEFAULT_TIME)
    Site_logo =models.ImageField(upload_to='static/logoimage',blank=True, \
    null=True)


    def __unicode__(self):
        return self.Company_Name

    class Meta:
        ordering = ('Company_Name',)

class Work_Type(Base):
    name = models.CharField(max_length = 100)
    active = models.IntegerField(blank=True, null=True, default=2)
    hourly_rate = models.FloatField(blank = True, null = True)
    #estimated_hours = models.FloatField(blank = True,null = True)
    #total = models.FloatField(blank = True,null = True)
    
    def __unicode__(self):
        return self.name

class Modules(Base):
    name = models.CharField(max_length=30)
    active = models.IntegerField(default=2)
    description = models.CharField(max_length=30, blank=True, null=True)
    global_module = models.IntegerField(default=0)


    def __unicode__(self):
        return self.name

class Task_Statuses(Base):
    name = models.CharField(max_length=40)
    active = models.IntegerField(default=2)

    def __unicode__(self):
        return self.name

class Task_priorities(Base):
    name = models.CharField(max_length=40)
    color = models.CharField(max_length=40)
    active = models.IntegerField(default=2)

    def __unicode__(self):
        return self.name

class Default_invoicing(Base):
    address = models.CharField(max_length=30)
    fine_print = models.CharField(max_length=40)
    next_number = models.CharField(max_length=40)
    term = models.CharField(max_length=40,choices=TERM_CHOICES)
    tax = models.CharField(max_length=40,blank=True,null=True)
    logo = models.ImageField(upload_to="static/images",blank=True,null=True)
    active = models.IntegerField(default=2)

    def __unicode__(self):
        return self.address

class Resource_Categorization(Base):
    name = models.CharField(max_length=100)
    active = models.IntegerField(default=2)

    def __unicode__(self):
        return self.name


class Project_categorization(Base):
    name = models.CharField(max_length=100)
    active = models.IntegerField(default=2)

    def __unicode__(self):
        return self.name




# Create your models here.
