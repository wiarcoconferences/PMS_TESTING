from django.db import models
from client.models import Base
#from thumbs import ImageWithThumbsField
from people.models import UserProfile

OPTIONAL = (('Yes', 'Yes'), ('NO', 'NO'))

class LeaveCalender(Base):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField()
    active = models.IntegerField(default=2)
    image = models.ImageField(upload_to='static/%Y/%m/%d', blank=True, null=True)
    optional = models.CharField(max_length=100, choices = OPTIONAL) 
#    optional = models.BooleanField()


    def __unicode__(self):
        return self.name
        
        
class Resource_LeaveCalender(Base):
    person = models.ForeignKey(UserProfile)
    description = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.IntegerField(default=0)

    def __unicode__(self):
        return self.description
