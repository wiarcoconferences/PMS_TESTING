from django.forms import *
from Events.models import *
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
class EventForm(ModelForm):
    class Meta:
        model = Event
        exclude = ['color', 'active', 'ngo', 'fundraisers', 'display', 'display_name', 'display_one', 'display_one_name','contributing_hotels','corporate_tables','small_image']

class event_ngo(forms.Form):
    ngo = forms.ModelMultipleChoiceField(queryset=NGO.objects.filter(active=True), required=False)

class event_corporate_tables(forms.Form):
    corporate_tables = forms.ModelMultipleChoiceField(queryset=Corporate_Tables.objects.filter(active=True), required=False)

class event_contributing_hotels(forms.Form):
    contributing_hotels = forms.ModelMultipleChoiceField(queryset=Contributing_Hotels.objects.filter(active=True), required=False)

def get_ftype_form(id):
    class event_fundraisercct20form(forms.Form):
        fundraiser = forms.ModelMultipleChoiceField(queryset=Fundraiser.objects.filter(active=True, fundraiser_type__id=id), required=False)
    return event_fundraisercct20form

def get_display_ftype_form(id):
    class event_diplayform(forms.Form):
        event_obj = Event.objects.get(id=id)
        fundraiser_type_list = event_obj.allowed_categories.all()
        name = forms.CharField(required=True)
        fundraiser_type = forms.ModelMultipleChoiceField(queryset=fundraiser_type_list, required=True)
    return event_diplayform

class EventArticleForm(ModelForm):
    class Meta:
        model = EventArticle
        exclude = ['content_type', 'slug', 'object_id', 'relatedTo', 'active']

class EventOverviewForm(ModelForm):
    class Meta:
        model = EventArticle
        exclude = ['content_type', 'slug', 'object_id', 'relatedTo', 'active', 'name', 'image', 'summary', 'display']

class EventAboutUsForm(ModelForm):
    class Meta:
        model = EventAboutUs
        exclude = ['event', 'active']

class EventContactUsForm(ModelForm):
    class Meta:
        model = EventContactUs
        exclude = ['event', 'active']

class EventBannerForm(ModelForm):
    class Meta:
        model = EventBanners
        exclude = ['content_type',  'object_id', 'relatedTo', 'active']
