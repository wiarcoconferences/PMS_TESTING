from django.forms import forms
from projects.models import *
from django import forms
from functools import partial
DateInput = partial(forms.DateInput, {'class': 'datepicker'})



class ProjectForm(forms.Form):

    name = forms.CharField()
    description = forms.CharField(widget=forms.Textarea(attrs={'cols':80, 'rows':6}), required=False)
    project_status  = forms.ChoiceField(choices = PROJECT_STATUS_TYPES, 
                                widget=forms.Select(attrs={'data-rel':'chosen'}),
                                                    required=False)
    start_date = forms.DateField(widget=DateInput("%Y-%m-%d"), required=False)
    end_date = forms.DateField(widget=DateInput("%Y-%m-%d"), required=False)
    budget = forms.FloatField(required=False)
    alert = forms.FloatField(required=False)
    client = forms.ModelChoiceField(queryset=Client.objects.all(), required=False, initial='No Client')
    project_manager = forms.ModelChoiceField(queryset=Project_Manager.objects.all().order_by('name'),
                                                        required=False)
    
class Project_ManagerForm(forms.ModelForm):

    class Meta:
        model = Project_Manager
        

