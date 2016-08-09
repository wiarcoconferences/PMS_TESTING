from django.db import models
from django import forms
from milestones.models import *
from tasks.models import *
from django.forms import ModelForm

def Milestone_Form(id):


    class MilestoneForm(ModelForm):
        available_task = forms.ModelMultipleChoiceField(queryset=Tasks.objects.filter(owned_by__user__id=id), required=False)
        title = forms.CharField(widget=forms.Textarea(attrs={'cols':100,'rows':1}), required=True)
        description = forms.CharField(widget=forms.Textarea(attrs={'cols': 95, 'rows': 2}), required=False)
        YESNO_CHOICES = ((False, 'In Progress'), (True, 'Complete'))
        status = forms.ChoiceField(choices = YESNO_CHOICES, widget = forms.RadioSelect, initial='False')
        person = UserProfile.objects.get(user_id=id)
        project_list = person.project.all()
        project_ids = [i.id for i in person.project.all()]
        project = forms.ModelChoiceField(queryset=Project.objects.filter(id__in=project_ids))
        client_ids = [i.client.id for i in person.project.all()]
        client = forms.ModelChoiceField(queryset=Client.objects.filter(id__in=client_ids))
        owned_by = forms.ModelChoiceField(queryset=UserProfile.objects.all(),\
                                    required=False)
        class Meta:
            model = Milestone
            exclude = ['activate',]
            widgets = {
                'due_date': forms.DateInput(attrs={'class':'datepicker'}),
            }
    return MilestoneForm


class Milestone_DocumentForm(ModelForm):


    class Meta:
        model = Milestone_Document
        exclude = ('milestone_documents',)


#widget=forms.Select(attrs={'data-rel':'chosen'}),
