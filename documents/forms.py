from django.forms import ModelForm
from django import forms
from documents.models import Document
from tasks.models import *

def Document_Form(id, postdict = {}, filedict = {} ):

    class DocumentForm(forms.Form):
        person = UserProfile.objects.get(user_id=id)
        title = forms.CharField(required=True)
        files = forms.FileField(label='Upload a Document',required=False)
        project_ids = [i.id for i in person.project.all()]
        project = forms.ModelChoiceField(queryset=Project.objects.filter(id__in=project_ids), empty_label='Choose a project')
        milestone = forms.ModelChoiceField(queryset=Milestone.objects.filter(owned_by__user__id=id), required=False)
        tasks = forms.ModelChoiceField(queryset=Tasks.objects.filter(owned_by__user__id=id, status='1'), required=False)
        tags = forms.CharField(required=False)
        notes = forms.CharField(widget=forms.Textarea(attrs={'cols': 100, 'rows': 5}), required=False)


        class Meta:
            model = Document
            exclude = ['content_type', 'objects_id', 'active', 'optional_information', 'tags']
    return DocumentForm



class TaskDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        exclude = ['content_type', 'objects_id', 'active', 'optional_information']
