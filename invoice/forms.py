from django.forms import ModelForm
from invoice.models import *
from django import forms



class InvoicesForm(forms.ModelForm):
    
    class Meta:
        model = Invoices
