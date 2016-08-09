from django import forms
from django.forms import widgets
from django.forms.extras.widgets import SelectDateWidget
from datetime import *
from django.db.models import Q
import re
from django.forms import ModelForm
from django.template.defaultfilters import slugify
from mcms.models import *
from NGO.models import *
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.conf import settings 
from ckeditor.widgets import CKEditorWidget
from Events.models import *

Size_CHOICES = ((u'S', 'Small'),(u'M', 'Medium'),(u'L', 'Large'),)
title_CHOICES = (('u''Mister', 'Mr.'),('u''Miss', 'Ms.'))
TITLE_CHOICES = (('u''Mr.', 'Mr.'),('u''M.s', 'Ms.'),('u''Miss.', 'Miss.'),('u''Mrs.', 'Mrs.'),('u''Dr.', 'Dr.'),('u''Colonel.', 'Colonel.'))
NEWS_CHOICES = (('', '---------'),('General news', 'General news'),('BC News','BC News'))

class LOGIN_FORM(forms.Form):
	username = forms.CharField(label=(u'Username '), required=False)
	password = forms.CharField(label=(u'Password '), widget=forms.PasswordInput(), required=False)

class UserForm(forms.ModelForm):
	class Meta:
		model = User
		exclude = ('groups', 'username', 'is_active','user_permissions', 'last_login', 'date_joined','is_staff','is_superuser','password')

class UserFormBk(forms.ModelForm):
	password = forms.CharField(label=(u'Password '), widget=forms.PasswordInput(), required=True)
	class Meta:
		model = User
		exclude = ('groups', 'username','user_permissions', 'is_active', 'last_login', 'date_joined','is_staff','is_superuser','password')
        fields = ['first_name','last_name','email']

class UserRegForm(forms.ModelForm):
	class Meta:
		model = User
		exclude = ('groups', 'user_permissions', 'last_login', 'date_joined','is_staff','is_superuser')


class UserProfile1Form(forms.ModelForm):
    first_name = forms.RegexField(label=("First Name*"), max_length=80, regex=r'^[a-zA-Z ]+$',error_message = ("It must contain only letters."),required=True)
    last_name = forms.RegexField(label=("Last Name*"), max_length=80, regex=r'^[a-zA-Z ]+$',error_message = ("It must contain only letters."),required=True)
    class Meta:
        model = User
        widgets = {'username':forms.TextInput(attrs={'readonly':'readonly'})}
        exclude = ('password', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'last_login', 'date_joined')


class UserProfile2Form(forms.ModelForm):
	city = forms.RegexField(label=("City*"), max_length=80, regex=r'^[a-zA-Z ]+$',error_message = ("It must contain only letters."),required=True)
	class Meta:
		model = UserProfile
		exclude = ('is_active', 'user')


class UserProfileEditForm(forms.Form):
	salutations_list = Salutations.objects.all()
	title = forms.ModelChoiceField(label=("Title*"), queryset=salutations_list, required=False)
	username= forms.CharField(label=(u'Username'),max_length=100,widget=forms.TextInput(attrs={'readonly':'readonly'}))
	first_name = forms.RegexField(label=("First Name*"), max_length=80, regex=r'^[a-zA-Z ]+$',error_message = ("It must contain only letters."),required=True)
	last_name = forms.RegexField(label=("Last Name*"), max_length=80, regex=r'^[a-zA-Z ]+$',error_message = ("It must contain only letters."),required=True)
	email = forms.EmailField(label=('E-mail Address*'), widget=forms.TextInput(attrs={'readonly':'readonly'}))
	address1 = forms.CharField(label=(u'Address Line1*'),max_length=100,required=True)
	address2 = forms.CharField(label=(u'Address Line2'),max_length=100,required=False)
#	address3 = forms.CharField(label=(u'Address Line3'),max_length=100,required=False)
#	ph_no = forms.RegexField(label=("Phone*"), max_length=10, regex=r'^[0-9 ]+$',error_message = ("It must contain only numbers."),required=True)
	city = forms.RegexField(label=("City*"), max_length=80, regex=r'^[a-zA-Z ]+$',error_message = ("It must contain only letters."),required=False)
	pincode = forms.RegexField(label=("Pincode*"), max_length=6, regex=r'^[0-9 ]+$',error_message = ("It must contain only numbers."),required=False)

class ChoiceForm(forms.Form):
	project = forms.CharField(label=(u'For a project '), required=False)
	ngo = forms.CharField(label=(u'For an NGO during TCS world 10 K Event '), required=False)

class LoginForm(forms.Form):
	username = forms.CharField(label=(u'Email Address:* '), required=True)
	password = forms.CharField(label=(u'Password:* '), widget=forms.PasswordInput(), required=True)

from django.core.files.images import get_image_dimensions
class ImageForm(ModelForm):
   class Meta:
       model=Image
       exclude=('content_type', 'object_id', 'title', 'listingOrder', 'status', 'active')
       def clean_picture(self):
           picture = self.cleaned_data.get("image")
           if not picture:
               raise forms.ValidationError("No image!")
           else:
               w, h = get_image_dimensions(picture)
               if w != 930:
                   raise forms.ValidationError("The image is %i pixel wide. It's supposed to be 930px" % w)
               if h != 300:
                   raise forms.ValidationError("The image is %i pixel high. It's supposed to be 300px" % h)
           return picture

# --------------------------- manage section forms -----------------------------------------------------#

class ArticleForm(ModelForm):
    class Meta:
        model = Article
        exclude = ('slug','block','team','staff','summary','listingOrder','status', 'active')

class OurEventsForm(forms.ModelForm):
    class Meta:
        model = Our_Events
        exclude = ('active')

class LinkForm(ModelForm):
    class Meta:
        model = Link
        exclude=('content_type', 'object_id', 'title', 'listingOrder', 'status', 'active')

class AttachmentForm(ModelForm):
    class Meta:
        model = Attachment
        exclude=('content_type', 'object_id', 'title', 'listingOrder', 'status', 'active')

class CodeForm(ModelForm):
    class Meta:
        model = CodeScript
        exclude=('content_type', 'object_id', 'status', 'active')

class CauseForm(forms.ModelForm):
    class Meta:
        model = Cause
        exclude = ('active', 'slug')

class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        exclude = ('active', 'description')

class HomeBannerForm(forms.ModelForm):
    class Meta:
        model = HomeBanner
        exclude = ('active')

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ('content_type','object_id', 'active', 'state','country')

class NeedForm(ModelForm):
    class Meta:
        model = Need
        exclude = ('content_type','object_id', 'active')

class VolunteerReqForm(ModelForm):
    class Meta:
        model = Volunteer_Requirements
        exclude = ('content_type','object_id', 'active')

class SectionForm(ModelForm):
    class Meta:
        model = Section
	exclude = ('active','slug','parent')

class Staff_typeForm(ModelForm):
    class Meta:
        model = Staff_Type
	exclude = ('slug','active')

class StaffForm(ModelForm):
    class Meta:
        model = Staff
	exclude = ('slug','active')

class NewsForm(ModelForm):
    class Meta:
        model = News
	exclude = ('active', 'name' , 'section', 'summary')

class NeedNgoForm(forms.Form):
    ngo = forms.ModelChoiceField(queryset=NGO.objects.filter(active=True),required=True)

class UserProfileForm7(ModelForm):
    class Meta:
        model = UserProfile
	exclude = ('active')

class UserInfoForm1(forms.Form):
    salutations_list = Salutations.objects.all()
    title = forms.ModelChoiceField(label=("Title*"), queryset=salutations_list, required=False)
    firstname = forms.RegexField(label=("First name*"), max_length=30,regex=r'^[a-zA-Z0-9 ]+$',error_message="It should be in letters")
    lastname = forms.RegexField(label=("Last name"), max_length=30,regex=r'^[a-zA-Z ]+$',error_message="It should be in letters" ,required=False)
    email = forms.CharField(label = 'Email* ',max_length=80)
    password1 = forms.CharField(label=("Password*"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=("Password verify*"), widget=forms.PasswordInput,
        help_text = ("Enter the same password as above, for verification."))
    address1 = forms.CharField(label = 'Address Line 1*',max_length=100)
    address2 = forms.CharField(label = 'Address Line 2*',max_length=100)
    city = forms.RegexField(label=("City*"), max_length=80, regex=r'^[a-zA-Z ]+$')
    pincode =forms.RegexField(label=("Pincode*"), max_length=6,regex=r'^[0-9 ]+$')

    def clean_username(self):
        username = self.cleaned_data["email"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(("The two password fields didn't match."))
        return password2

class Contibuting_HotelsForm(ModelForm):
    class Meta:
        model = Contributing_Hotels
        exclude = ('active', 'slug')
    
class Corporate_TablesForm(ModelForm):
    class Meta:
        model = Corporate_Tables
        exclude = ('active', 'slug')

class ContactUsForm(ModelForm):
    class Meta:
        model = Contactus
        exclude = ('active')

class Duplicate_CorporatesForm(forms.ModelForm):
    class Meta:
        model = Duplicate_Corporates
        exclude = ('active')
