from leavecalender.models import *
from django.forms import *
from django import forms

OPTIONAL = (('Yes', 'Yes'), ('No', 'NO'))

class LeaveCalenderForm(forms.Form):

    name = forms.CharField(max_length=100, required=True)
    description = forms.CharField(max_length=100, required=False)
    date = forms.DateField()
    image = forms.ImageField(label='Upload a Image',required=False)
    optional = forms.ChoiceField(required=False, widget=forms.RadioSelect, choices=OPTIONAL)
    #optional = forms.ChoiceField(choices = OPTIONAL, widget = forms.RadioSelect, initial='True')



class Meta:
        model = LeaveCalender
        exclude = ('active')


class Resource_LeaveCalenderForm(forms.Form):


    person = forms.ModelChoiceField(queryset=UserProfile.objects.all(), required=True)
    description = forms.CharField(required=False, max_length=100)
    start_date = forms.DateField()
    end_date = forms.DateField()

    class Meta:
        model = Resource_LeaveCalender
        exclude = ('active')
