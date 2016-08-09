from django.db import models
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
# Create your models here.

class Register(models.Model):
    firstname = models.CharField(max_length='10')
    lastname = models.CharField(max_length='10')
    email = models.EmailField()
    address1 = models.CharField(max_length='10')
    address2 = models.CharField(max_length='10')
    mobile = models.IntegerField(max_length='10')


    def __unicode__(self):
        return self.firstname


# Create your models here.
