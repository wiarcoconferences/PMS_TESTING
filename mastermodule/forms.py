

from django.forms import forms
from mastermodule.models import *
from django import forms

class Work_TypeForm(forms.ModelForm):

    class Meta:
        model = Work_Type
        exclude = ('active',)

class ModulesForm(forms.Form):
    name = forms.CharField(max_length=40)
    description = forms.CharField(max_length=40, required=False)


class Task_StatusesForm(forms.Form):
    name = forms.CharField(max_length=40)


class Task_PrioritiesForm(forms.Form):
    name = forms.CharField(max_length=40)
    color = forms.CharField(max_length=30, required=False)


class Resource_CategorizationForm(forms.Form):
    name = forms.CharField(max_length=100)


class Project_categorizationForm(forms.Form):
    name = forms.CharField(max_length=100)


class GeneralinfoForm(forms.ModelForm):


    class Meta:
        model = Generalinfo
