from django.db import models
from django import forms
from models import *
from django.forms import ModelForm


def Task_Formf(id):

    class TaskForm(ModelForm):
        title = forms.CharField(widget=forms.Textarea(attrs={'cols':100,'rows':1}),required=True)
        person = UserProfile.objects.get(user_id=id)
        project = person.project.all()
        project_ids = [i.id for i in person.project.all()]
        project = forms.ModelChoiceField(queryset=Project.objects.filter(id__in=project_ids))
        client_ids = [i.client.id for i in person.project.all()]
        client = forms.ModelChoiceField(queryset=Client.objects.filter(id__in=client_ids))
        
        userprofile_ids = []
        
        usp = UserProfile.objects.filter(project__id__in = project_ids)
        for j in usp:
            userprofile_ids.append(j.id)
        #milestone = Milestone.objects.filter(owned_by__user__id=id)
        assigned_to = forms.ModelMultipleChoiceField(queryset=UserProfile.objects.filter(id__in = list(set(userprofile_ids))), required=False)
        followed_by = forms.ModelMultipleChoiceField(queryset=UserProfile.objects.filter(id__in = list(set(userprofile_ids))), required=False)
        milestone = forms.ModelChoiceField(queryset=Milestone.objects.filter(owned_by__user__id=id), required=False)
        status = forms.ModelChoiceField(queryset=Task_Statuses.objects.filter(active=2), initial='Open')
        priority = forms.ModelChoiceField(queryset=Task_priorities.objects.all(), initial={'Medium'})
        summary = forms.CharField(widget=forms.Textarea(attrs={'cols': 105, 'rows': 1}), required=False)
        class Meta:
            model = Tasks
            widgets = {
            'due_date': forms.DateInput(attrs={'class':'datepicker'}),
            'start_date': forms.DateInput(attrs={'class':'datepicker'}),
            }
    return TaskForm


def Request_Formf(id):

    class RequestForm(ModelForm):

        title = forms.CharField(widget=forms.Textarea(attrs={'cols':110,'rows':1}),required=True)
        person = UserProfile.objects.get(user_id=id)
        project = person.project.all()
        project_ids = [i.id for i in person.project.all()]
        project = forms.ModelChoiceField(queryset=Project.objects.filter(id__in=project_ids))
        client_ids = [i.client.id for i in person.project.all()]
        client = forms.ModelChoiceField(queryset=Client.objects.filter(id__in=client_ids))

        class Meta:
            model = Request
            widgets = {
            'requested_due_date': forms.DateInput(attrs={'class':'datepicker'}),
            }
    return RequestForm
        
