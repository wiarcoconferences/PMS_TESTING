from django import forms
from django.forms import widgets
from models import Register

class AddForm(forms.Form):
    username = forms.EmailField()
    password = forms.CharField(widget = forms.PasswordInput)
    retypepassword = forms.CharField(widget = forms.PasswordInput)


class NameForm(forms.ModelForm):
    username = forms.EmailField()
    password = forms.CharField(widget = forms.PasswordInput)
    retypepassword = forms.CharField(widget = forms.PasswordInput)  


    class Meta:
        model = Register
        exclude = ('user',)
        widgets = {
            'password': forms.PasswordInput(),
            'retypepassword' : forms.PasswordInput(),
            'number':forms.TextInput(attrs={'type':'text'})
        }



