from django.db import models
from django import forms
from times.models import *
from django.forms import ModelForm



def Time_Form(id):

    class AddTimeForm(ModelForm):
        tasks = forms.ModelChoiceField(queryset=Tasks.objects.filter(owned_by__user__id=id, status='1'), required=False)
        person = UserProfile.objects.get(user_id=id)
        project_ids = [i.id for i in person.project.all()]
        project = forms.ModelChoiceField(queryset=Project.objects.filter(id__in=project_ids), empty_label='Choose a project')
        client_ids = [i.client.id for i in person.project.all()]
        client = forms.ModelChoiceField(queryset=Client.objects.filter(id__in=client_ids), empty_label='Choose a client')
        description = forms.CharField(widget=forms.Textarea(attrs={'cols': 105, 'rows': 2}), required=False)
        billable = forms.BooleanField(widget = forms.CheckboxInput, initial='True')
        class Meta:
            model = AddTime
            exclude = ['status_view', 'project', 'client', ]
            widgets = {
                'pub_date': forms.DateInput(attrs={'class': 'datepicker'}),
            }
    return AddTimeForm
