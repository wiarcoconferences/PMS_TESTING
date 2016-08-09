from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from thumbs import ImageWithThumbsField
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User,UserManager

NAME_PREFIX_CHOICES = (('Mr.','Mr'), ('Ms.','Ms'),('Mis','Miss'),('Mrs','Mrs'),('Dr','Dr'),('Sr','Sr'),('Col','Colonel'))
GENDER_CHOICES = ( (u'M', u'Male'), (u'F', u'Female'),)
USERTYPE_CHOICES = ( (u'1', u'NGO'), (u'2', u'Individual'),(u'3', u'Fundraiser'),)


class Base(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Country(Base):
    name = models.CharField('Country Name', max_length=400)

    def __unicode__(self):
        return self.name


class State(Base):
    country = models.ForeignKey(Country)
    name = models.CharField('State Name', max_length=400)

    def __unicode__(self):
        return self.name


class Section(Base):
    name = models.CharField('Name', max_length=200)
    icon = ImageWithThumbsField(upload_to = 'static/%Y/%m/%d', sizes=((90,120),(180,240),(360,480)),blank=True,  null=True )
    description = RichTextField(blank=True, null = True)
    slug = models.SlugField("SEO friendly url, use only aplhabets and hyphen", max_length=60)
    parent = models.ForeignKey('self', blank=True, null=True)


    def __unicode__(self):
        return self.name

    def get_section_images(self):
        return Image.objects.filter(content_type__name__iexact="Section",object_id=self.id)

    def get_section_atachment(self):
        return Attachment.objects.filter(content_type__name="section",object_id=self.id)

    def get_section_links(self):
        return Link.objects.filter(content_type__name="section",object_id=self.id)
      
    def get_section_codes(self):
        return CodeScript.objects.filter(content_type__name="section",object_id=self.id)


class Article(Base):
    name = models.CharField('Name', max_length=200)
    section = models.ForeignKey(Section,blank=True,null=True)
    summary = models.CharField("Byline/ Summary", blank=True, null=True, max_length=400)
    description = RichTextField()
    image = ImageWithThumbsField(upload_to = 'static/%Y/%m/%d', sizes=((90,120),(180,240),(287,124),(360,480)),blank=True,  null=True )
    slug = models.SlugField("SEO friendly url, use only aplhabets and hyphen", max_length=60)

    def __unicode__(self):
        return self.name

    def get_article_images(self):
        return Image.objects.filter(content_type__name__iexact="article",object_id=self.id)

    def get_article_atachment(self):
        return Attachment.objects.filter(content_type__name="article",object_id=self.id)

    def get_article_links(self):
        return Link.objects.filter(content_type__name="article",object_id=self.id)

    def get_article_codes(self):
        return CodeScript.objects.filter(content_type__name="article",object_id=self.id)


class News(Base):
    event = models.ForeignKey('Events.Event',blank=True,null=True)
    name = models.CharField('Name', max_length=200)
    section = models.ForeignKey(Section,blank=True,null=True)
    summary = models.CharField("Byline/ Summary", blank=True, null=True, max_length=400)
    description = RichTextField(blank = True, null = True)
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_to = models.DateTimeField(blank=True, null=True)


    def __unicode__(self):
        return self.name

SITE_CHOICES = ( (u'general', u'general'), (u'event', u'event'))
class Gallery(Base):
    choice = models.CharField(max_length=100, choices=SITE_CHOICES)
    event = models.ForeignKey('Events.Event', blank=True, null=True)
    name = models.CharField(max_length=60)
    description = RichTextField(blank=True, null=True)
    front_image = ImageWithThumbsField(upload_to='static/%Y/%m/%d', sizes=((90,120),(180,240),(360,480)),blank=True,  null=True)
    link = models.CharField('Url for album', max_length=500,blank=True, null=True )

    def __unicode__(self):
        return self.name

    def get_images(self):
        return Image.objects.filter(content_type__name__iexact="gallery",object_id=self.id, active=True)

class CodeScript(Base):
    name = models.CharField(max_length=60)
    description = models.TextField("Code to be inserted", 
                        blank=True, null=True, max_length=800)
    content_type = models.ForeignKey(ContentType,
                    verbose_name=_('content type'),
                    related_name="content_type_set_for_%(class)s")
    object_id = models.TextField(_('object ID'))
    relatedTo = generic.GenericForeignKey(ct_field="content_type", fk_field="object_id")

    def __unicode__ (self):
        return self.name



class Attachment(Base):
    name = models.CharField(max_length=60)
    attach_file = models.FileField(upload_to='static/%Y/%m/%d', blank=True, null=True)
    description = models.CharField("Description", blank=True, null=True, max_length=300)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id = models.TextField(_('object ID'))
    relatedTo = generic.GenericForeignKey(ct_field="content_type", fk_field="object_id")

    def __unicode__(self):
        return self.name



class Image(Base):
    image = ImageWithThumbsField(upload_to='static/%Y/%m/%d', sizes=((90,120), (100,100),(120,120),(180,240),(360,480),(930,300)),blank=True,null=True,help_text=("Image size should be 930x300 pixels"))
    name = models.CharField("Caption * ", blank=True, null=True, max_length=50)
    description = models.CharField("Description", blank=True, null=True, max_length=300)
    URL = models.URLField("Link url", max_length=200, blank=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id = models.TextField(_('object ID'))
    relatedTo = generic.GenericForeignKey(ct_field="content_type", fk_field="object_id")


    def __unicode__(self):
        return '%s'%(self.name)



class Link(Base):
    """ Class describes cms links """
    name = models.CharField(max_length=100)
    image = ImageWithThumbsField(upload_to='static/%Y/%m/%d', sizes=((90,
                                 120), (180, 240), (360, 480)), blank=True,
                                 null=True)
    URL = models.CharField('Link url', max_length=200, blank=True)
    description = models.CharField('Description', blank=True, null=True,
                                   max_length=300)
    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_('content type'),
                                     related_name='content_type_set_for_%(cla'
                                     'ss)s')
    object_id = models.TextField(_('object ID'))
    relatedTo = generic.GenericForeignKey(ct_field='content_type',
            fk_field='object_id')


    def __unicode__(self):
        return self.name


class Address(Base):
    address1 = models.CharField('Address1', max_length = 100, blank=True, null=True)
    address2 = models.CharField('Address2', max_length = 100, blank=True, null=True)
    country = models.ForeignKey('Country', blank = True, null = True)
    state = models.ForeignKey('State', blank = True, null = True)
    city = models.CharField('City', max_length = 100, blank=True, null=True)
    mobile = models.CharField('Mobile', max_length = 100, blank=True, null=True)
    pincode = models.CharField('Pincode', max_length = 100, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id = models.TextField(_('object ID'))
    relatedTo = generic.GenericForeignKey(ct_field="content_type", fk_field="object_id")


    def __unicode__(self):
        return "%s - %s - %s" %(self.state, self.city, self.address1)


class Staff_Type(Base):
    name=models.CharField(max_length=60)
    slug = models.SlugField("SEO friendly url, use only aplhabets and hyphen",max_length=60)

    def __unicode__(self):
        return self.name

    def get_trustees(self):
        return Staff.objects.filter(staffType__slug = 'trustees', active = True)

    def get_staffs(self):
        return Staff.objects.filter(staffType__slug = 'staff', active = True)


class Staff(Base):
    prefix = models.CharField("Prefix *", max_length=10, choices=NAME_PREFIX_CHOICES)
    name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField("Gender *", max_length=1, choices=GENDER_CHOICES)
    staffType = models.ForeignKey('Staff_type', blank=True, null=True)
    slug = models.SlugField("SEO friendly url, use only aplhabets and hyphen *", max_length=60)
    summary = models.CharField("summary", blank=True, null=True, max_length=200)
    profile_text = RichTextField(blank=True, null = True)
    image = models.ImageField(upload_to='static/%Y/%m/%d', blank=True, null=True )
    webURL = models.URLField("Web URL", blank=True, null=True, max_length="60")
    display_order = models.PositiveIntegerField('Displaying order', blank=True, null=True)

    def __unicode__(self):
        return u'%s %s '%(self.prefix, self.name)

class Event_Type(Base):
    name = models.CharField(max_length=100)
    slug = models.SlugField("SEO friendly url, use only aplhabets and hyphen",max_length=60)

    def __unicode__(self):
        return self.name



class Our_Events(Base):
    event_type = models.ForeignKey(Event_Type)
    name = models.CharField('Event Name', max_length=200)
    start_year = models.DateField(blank=True,null=True)
    end_year = models.DateField(blank=True,null=True)
    amount_raised = models.PositiveIntegerField()
    description = RichTextField(blank=True, null=True)
    image = ImageWithThumbsField(upload_to = 'static/images/%Y/%m/%d', sizes=((90,120),(180,240),(360,480)),blank=True,  null=True )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Our Events'

class Salutations(Base):
    name = models.CharField('Name*', max_length=100)

    def __unicode__(self):
        return self.name

class UserProfile(Base):
    title = models.ForeignKey(Salutations, blank=True, null=True)
    user = models.ForeignKey(User)
    usertype = models.CharField("UserType ", max_length=100, choices=USERTYPE_CHOICES, blank=True, null=True)


    def __unicode__(self):
        if not self.user.username:
            return self.user.first_name
        else:
            return self.user.username

class UserDetails(Base):
    user = models.ForeignKey(User)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    def __unicode__(self):
        return self.username


class IndividualActivation(models.Model):
    user = models.ForeignKey(User)
    activation_key = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    def __unicode__(self):
            return self.user.username

class Invite(Base):
    name = models.CharField("NGO Name",max_length=100)
    url = models.URLField("NGO Website Link", max_length=200,blank=True,null=True)
    contact_person = models.CharField("NGO Contact Person ",max_length=100,blank=True,null=True)
    email = models.EmailField("NGO Email Id *")
    phone = models.CharField("NGO Contact Number ", max_length=15,blank=True,null=True)
    your_name = models.CharField("Your Name *",max_length=100)
    your_email = models.EmailField("Your Email Id *")
    comments = models.TextField("Your message to the NGO",blank=True,null=True)

    def __unicode__(self):
        return self.name


class HomeBanner(Base):
    name = models.CharField("Image name",max_length=100)
    image = ImageWithThumbsField(upload_to = 'static/images/%Y/%m/%d', 
                                    sizes=((90, 120), (180, 240), (360, 480), 
                                    (1200, 556)), blank=True, null=True)

    def __unicode__(self):
        return self.name

class Requests(Base):
    name = models.CharField('Name', max_length=400,blank=True,null=True)
    email = models.EmailField("Email*", max_length=100,blank=True,null=True)
    phone = models.CharField(max_length=15,blank=True,null=True)
    message = models.CharField(max_length=500,blank=True,null=True)

    def __unicode__(self):
        return self.name

class Contactus(Base):
    summary = models.CharField('Summary', max_length=400,blank=True,null=True)
    description = RichTextField(blank=True, null = True)
    phone1 = models.CharField('Phone1', max_length=15,blank=True,null=True)
    phone2 = models.CharField('Phone2', max_length=15,blank=True,null=True)
    phone3 = models.CharField('Phone3', max_length=15,blank=True,null=True)
    mobile1 = models.CharField('Mobile1', max_length=15,blank=True,null=True)
    mobile2 = models.CharField('Mobile2', max_length=15,blank=True,null=True)

    def __unicode__(self):
        return self.summary

    def get_address(self):
        return Address.objects.filter(content_type__name__iexact="contactus",object_id=self.id)
