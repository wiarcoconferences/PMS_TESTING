from django.forms import ModelForm
from client.models import Client
from django import forms
from django.forms import widgets

class ClientForm(forms.Form):
    name = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea(attrs={'cols': 95, 'rows': 5}), required=False)
    address = forms.CharField(max_length=100, label='address', required = False)
    email = forms.EmailField(max_length=100, required=False)
    phone = forms.CharField(max_length=12, required=False)
    website = forms.URLField(max_length=100, required=False)
    fax = forms.CharField(max_length=20, required=False)



