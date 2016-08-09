from django.forms import ModelForm
from people.models import *
from django import forms
from django.forms import widgets
from projects.models import *
import datetime
from django.utils.timezone import utc
from suit.widgets import AutosizedTextarea



class UserForm(forms.Form):
    title = forms.CharField(required=False, widget=forms.Select(choices=Title_choices))
    first_name = forms.CharField()
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}),required=False)
    phone = forms.CharField(required=False)
    #website = forms.URLField(required=False)
    #network = forms.CharField(required=False)
    #notes = forms.CharField(required=False)
    profile_image = forms.ImageField(label='Profile Image',required=False)
    client = forms.ModelChoiceField(queryset=Client.objects.all(),required=False)
    access_level = forms.CharField(max_length=30,widget=forms.Select(choices=Access_Level_CHOICES))
    project = forms.ModelMultipleChoiceField(queryset=Project.objects.all(),label='Project Permission',required=False)
    resource_categorization = forms.ModelChoiceField(queryset=Resource_Categorization.objects.all(),required=False)

    class Meta:
        model = UserProfile
        exclude = ('user','uuid', 'network', 'website', 'notes')

class UserEditForm(forms.Form):
    title = forms.CharField(required=False, widget=forms.Select(choices=Title_choices))
    first_name = forms.CharField()
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
    phone = forms.CharField(required=False)
    #website = forms.URLField(required=False)
    #network = forms.CharField(required=False)
    #notes = forms.CharField(required=False)
    profile_image = forms.ImageField(label='Profile Image',required=False)
    client = forms.ModelChoiceField(queryset=Client.objects.all(),required=False)
    access_level   = forms.CharField(max_length=30,
                widget=forms.Select(choices=Access_Level_CHOICES))
    project = forms.ModelMultipleChoiceField(queryset=Project.objects.all(),label='Project Permission',required=False)
    resource_categorization = forms.ModelChoiceField(queryset=Resource_Categorization.objects.all(),required=False)
    class Meta:
        model = UserProfile
        exclude = ('user',)


class LoginForm(forms.Form):
    username = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    retypepassword = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = UserProfile
        exclude = ('user',)
        widgets = {
            'password': forms.PasswordInput(),
            'retypepassword' : forms.PasswordInput(),
        }

    '''
class EmployeeForm(forms.Form):
    user = forms.ModelChoiceField(queryset=UserProfile.objects.all(),required=True)
    designation = forms.CharField(max_length=40,widget=forms.Select(choices=Designation_CHOICES))
    project_permission = forms.ModelMultipleChoiceField(queryset = Project.objects.all().order_by('name'),\
    required=False,widget=forms.CheckboxSelectMultiple)


class EmployerForm(forms.ModelForm):
    
    class Meta:
        model = Employer
    '''


