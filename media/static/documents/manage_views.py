from django.shortcuts import render_to_response, get_object_or_404
from django.utils.encoding import smart_str, smart_unicode
from django.contrib.auth.models import *
from django.contrib.auth import authenticate, login, logout
from django.template import Context, loader,RequestContext
from django.http import HttpResponseRedirect,HttpResponse,Http404
from django.template.defaultfilters import slugify
from datetime import *
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage, BadHeaderError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import password_reset
from mcms.models import *
from mcms.forms import *
from Projects.forms import *
from NGO.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.contenttypes.models import ContentType
from NGO.forms import *
from faq.models import *
from Events.forms import *
from Events.models import *
from csr.models import *
from csr.forms import *
import csv
import json
limit=20

def has_changed(instance, field):
    if not instance.pk:
        return False
    old_value = instance.__class__._default_manager.\
        filter(pk=instance.pk).values(field).get()[field]
    return not getattr(instance, field) == old_value

def userid():
    return uuid4().hex

def write_excel(excelStr,filename):         #To Generate Excel Sheets
    response = HttpResponse(excelStr, mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s.xls' %(str(filename))
    return response

def fundraiser_ajax(request):
    results ={}
    if request.is_ajax():
        fundraiser_type=request.GET.get("id")
        if fundraiser_type:
            funderobj=FundraiserType_details.objects.get(ftype__id=fundraiser_type)
            results['res']=funderobj.enter_in_digits
            return HttpResponse(json.dumps(results), mimetype="application/json")
    return render_to_response('manage/add_fundraise.html', locals(), context_instance=RequestContext(request))

def pagination(request, plist):
    paginator = Paginator(plist, 10)
    page = request.GET.get('page', '')
    try:
        plist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        plist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        plist = paginator.page(paginator.num_pages)
    return plist


def event_ngo_online_donations(eid, ngoid):
    # getting event wise online donations
    return Donation.objects.filter(event__id= eid, ngo__id=ngoid, payment_status= "Success")

def event_ngo_offline_donations(eid, ngoid):
    # getting event wise offline donations
    event = Event.objects.get(id=int(eid))
    funds = event.fundraisers.filter(ngo__id=int(ngoid))
    offline_donations = []
    for i in funds:
        if i.get_offline_donations():
            for j in i.get_offline_donations():
                offline_donations.append(j)
    return offline_donations

def adminlogin(request, next=''):
    user = request.user
    if request.method == 'POST':
        form = LOGIN_FORM(request.POST)
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            if user.is_superuser:
                login(request, user)
                # success        
                return HttpResponseRedirect('/manage_sections_home/') 
            else:
            # disabled account
                form = LOGIN_FORM()
                message = 'Please enter a correct username and password or You dont have Priviledge to Access this site.'
                return render_to_response('manage/login.html', locals(), context_instance=RequestContext(request))
        else:
            # invalid login
            form = LOGIN_FORM()
            message = 'Please enter a correct username and password'
            return render_to_response('manage/login.html', locals(), context_instance=RequestContext(request))
    else:
        form = LOGIN_FORM()
        return render_to_response('manage/login.html',{'user':user,'form':form},context_instance=RequestContext(request))   
    return render_to_response('manage/login.html', {'form':form}, context_instance=RequestContext(request))

def adminlogout (request):
    logout(request)    
    return HttpResponseRedirect ("/manage-login/")

def reset_password(request):
    q = request.GET.get('q')
    user_obj = User.objects.get(email=q)
    new_pwd = request.POST.get('new_pwd')
    chg_pwd = request.POST.get('chg_pwd')
    if new_pwd and chg_pwd:
        if request.method == 'POST':
            try:
                user_det = UserDetails.objects.get(user=user_obj)
            except:
                user_det = UserDetails.objects.create(user=user_obj)
            user_obj.set_password(chg_pwd)
            user_obj.save()
            user_det.username = user_obj.username
            user_det.password = new_pwd
            user_det.save()
            changed = True
    return render_to_response('manage/change-password.html', locals(), context_instance=RequestContext(request))

def home(request):
    user = request.user
    today = date.today()
    if user.id is not None and user.is_superuser:
        p=date.today()+timedelta(-1)
        #new_ngo=NGO.objects.filter(created_on__range=(p,today))
        #new_ngo = NGO.objects.filter(created_on__year=today.year,created_on__month=today.month,created_on__day=today.day)
        new_individual = UserProfile.objects.filter(created_on__range=(p,today+timedelta(1)) )
        #new_corporates = Corporate.objects.filter(created_on__range=(p,today+timedelta(1)))
        #updated_ngo = NGO.objects.filter(modified_on = today)
        #updated_ngo=NGO.objects.filter(modified_on__year=today.year,modified_on__month=today.month,modified_on__day=today.day)
        #updated_ngo = NGO.objects.filter(modified_on__range=(p,today+timedelta(1)))
        #updated_individual = UserProfile.objects.filter(modified_on__range=(p,today+timedelta(1)))
        #updated_corporates = Corporate.objects.filter(modified_on__range=(p,today+timedelta(1)))
        #applied_volunteer = Apply_volunteer.objects.filter(applied_on__range=(p,today+timedelta(1)))
        #applied_jobs = Apply_Job.objects.filter(created_on__range=(p,today+timedelta(1)))
        return render_to_response('manage/base.html',locals(), context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/adm-login')


def get_event_ngo_online_donations(eid, ngoid):
    amt = 0
    d= Donation.objects.filter(event__id= eid, ngo__id=ngoid, payment_status= "Success")
    for i in d:
        amt = amt + i.amount
    return amt


def get_event_ngo_offline_donations(eid, ngoid):
    # getting event wise offline donations
    amt = 0
    event = Event.objects.get(id=int(eid))
    funds = event.fundraisers.filter(ngo__id=int(ngoid))
    offline_donations = []
    for i in funds:
        if i.get_offline_donations():
            for j in i.get_offline_donations():
                offline_donations.append(j)
    for i in offline_donations:
        amt = amt + i.amount
    return amt


@login_required(login_url='/manage-home/')
def manage(request):
    fundraisers =[]
    key = request.GET.get('key', '')
    objects_list = ''
    item_list = ''
    if key == 'ourevents':
        event_list = Our_Events.objects.all()
        item_list = pagination(request, event_list)
        event_type = Event_Type.objects.filter(active = True)
        keyword = request.GET.get('keyword')
        startDate = request.GET.get('start_date')
        endDate = request.GET.get('end_date')
        status_name = request.GET.get('status_name')
        event_type_id = request.GET.get('event_type')
        if event_type_id:
            event_obj = Event_Type.objects.get(id = event_type_id)
            event_list = event_list.filter(event_type = event_obj)
        if status_name == "True":
            event_list = event_list.filter(active=True)
        if status_name == "False":
            event_list = event_list.filter(active=False)
        if keyword:
            event_list = event_list.filter(name__istartswith=keyword)
        if startDate:
            event_list = event_list.filter(start_year=startDate)
        if endDate:
            event_list = event_list.filter(end_year=endDate)
        item_list = event_list
        title = "Our Events"
    if key == 'cause':
        cause_list = Cause.objects.all()
        item_list = pagination(request, cause_list)
        keyword = request.GET.get('keyword')
        status_name = request.GET.get('status_name')
        if status_name == "True":
            cause_list = cause_list.filter(active=True)
        if status_name == "False":
            cause_list = cause_list.filter(active=False)
        if keyword:
            cause_list = cause_list.filter(name__istartswith=keyword)
        item_list = cause_list
        title = "Cause"
    if key == 'advertisement':
        events_list = Our_Events.objects.all()
        item_list = pagination(request, events_list)
        title = 'Event'
        event_type = Event_Type.objects.filter(active = False)
    if key =='faq':
        cat_list = FAQ_Category.objects.all()
        status_name = request.GET.get('status_name')
        keyword=request.GET.get('keyword')
        if status_name == "True":
            cat_list = cat_list.filter(is_active=True)
        if status_name == "False":
            cat_list = cat_list.filter(is_active=False)
        if keyword:
            cat_list = cat_list.filter(name__istartswith=keyword)
        faq_list = Question.objects.all()[:limit]
        item_list = cat_list
        title="Faq Category"
    if key =="activity-list" :
        act_id=request.GET.get('act_id')
        activities = Activity.objects.filter(activity_type = act_id)
        item_list = activities
        title= "Activity"
    if key =="manage-faq":
        faq_id=request.GET.get('faq_id')
        faq_obj = FAQ_Category.objects.get(id=faq_id)
        quest_list = Question.objects.filter(category=faq_obj)
        item_list = quest_list
        title = "Question and Answer"
    if key == 'section':
        section_list = Section.objects.all()
        status_name = request.GET.get('status_name')
        keyword=request.GET.get('keyword')
        if status_name == "True":
            section_list = section_list.filter(active=True)
        if status_name == "False":
            section_list = section_list.filter(active=False)
        if keyword:
            section_list = section_list.filter(name__icontains=keyword)
        item_list = section_list
        title = 'Section'
    if key == 'manage-sections':
        art_id = request.GET.get('art_id')
        get_section = Section.objects.get(id = art_id)
        title = "Section Items"
    if key == 'gallery':
        gal_list = Gallery.objects.all()
        title = "Gallery"
    if key == 'article':
        article_list = Article.objects.all()
        section_id = request.GET.get('section_name')
        status_name =request.GET.get('status_name')
        section_id = request.GET.get('section_name')
        keyword=request.GET.get('keyword')
        if status_name == "True":
            article_list = article_list.filter(active=True)
        if status_name == "False":
            article_list = article_list.filter(active=False)
        if keyword:
            if len(keyword)<=2:
                article_list = article_list.filter(name__istartswith=keyword)
            else:
                article_list = article_list.filter(name__icontains=keyword)
        if section_id:
            article_list = article_list.filter(section__id=section_id)
        section_list = Section.objects.all()
        item_list = article_list
        title = "Article"
    if key == "manage-articles":
        art_id = request.GET.get('art_id')
        article_lists = Article.objects.filter(id = art_id)
        get_article = Article.objects.get(id = art_id)
        item_list = article_lists
        title = "Article Items"
        img_title = "Images"
        attach_title = "Attachments"
        link_title = "Links"
        code_title = "Codes"
    if key == 'donation':
        donation_list = Donation.objects.filter(payment_status='Pending')
        item_list = pagination(request, donation_list)
        ngos_list = NGO.objects.filter(active=2)
        keyword = request.GET.get('keyword')
        startDate = request.GET.get('start_date')
        endDate = request.GET.get('end_date')
        status_name = request.GET.get('status_name')
        atype = request.GET.get('atype')
        ngo_id = request.GET.get('ngo_name')
        if status_name:
            donation_list = donation_list.filter(payment_status = status_name)
        if status_name == "False":
            donation_list = donation_list.filter(active=False)
        if keyword:
            donation_list = donation_list.filter(first_name__istartswith=keyword)
        if startDate and endDate:
            donation_list = donation_list.filter(created_on__gte=startDate, created_on__lte=endDate)
        if atype:
            donation_list = donation_list.filter()
        if ngo_id:
            ngo_obj = ngos_list.get(id=ngo_id)
            donation_list = donation_list.filter(ngo=ngo_obj)
        item_list = donation_list
        title = "Donation"

    if key == "corporate":
        item_list = CSR.objects.all()
        keyword = request.GET.get('keyword')
        status_name = request.GET.get('status_name')
        if keyword:
            item_list = item_list.filter(name__istartswith=keyword)
        if status_name == 'True':
            item_list = item_list.filter(active = True)
        if status_name == 'False':
            item_list = item_list.filter(active = False)
        title = 'Corpoartes'
    if key =='ngo':
        ngos_list = NGO.objects.all().order_by('name')
        event_list = Event.objects.filter(active=True).order_by('name')
        select_cause = request.GET.get('cause_name')
        status_name = request.GET.get('status_name')
        event_id = request.GET.get('event')
        ngo_name = request.GET.get('name')
        if event_id:
            ev=event_list.get(id=event_id)
            ngos_list = ev.ngo.filter(active=True)
        if status_name == "True":
            ngos_list = ngos_list.filter(active=True)
        if status_name == "False":
            ngos_list = ngos_list.filter(active=False)
        if select_cause:
            ngos_list=ngos_list.filter(cause__id=select_cause)
        if ngo_name:
            if len(ngo_name)<=2:
                ngos_list = ngos_list.filter(name__istartswith=ngo_name)
            else:
                ngos_list = ngos_list.filter(name__icontains=ngo_name)
        item_list = ngos_list
        cause_list = Cause.objects.all().order_by('name')
        title="NGO"
    if key == "manage-ngos":
        ngo_id = int(request.GET.get('ngo_id'))
        get_ngo = NGO.objects.get(id=ngo_id)
        img_title = "NGO Images"
    if key == 'advertisement':
        choice=''
        advertisement_list = Ads.objects.all()
        status_name =request.GET.get('status_name')
        keyword=request.GET.get('keyword')
        if status_name == "True":
            advertisement_list = advertisement_list.filter(active=True)
        if status_name == "False":
            advertisement_list = advertisement_list.filter(active=False)
        if keyword:
            advertisement_list = advertisement_list.filter(name__istartswith=keyword)
        item_list = advertisement_list
        title = "Advertisement"

    if key == 'activity':
        activity_list = Activity.objects.all()
        status_name = request.GET.get('status_name')
        keyword=request.GET.get('keyword')
        if status_name == "True":
            activity_list = activity_list.filter(active=True)
        if status_name == "False":
            activity_list = activity_list.filter(active=False)
        if keyword:
            activity_list = activity_list.filter(title__istartswith=keyword)
        item_list = activity_list
        title = "Activity"
    if key =='gallery':
        gallery_list= Gallery.objects.all()
        status_name = request.GET.get('status_name')
        keyword=request.GET.get('keyword')
        if status_name == "True":
            gallery_list = gallery_list.filter(active=True)
        if status_name == "False":
            gallery_list = gallery_list.filter(active=False)
        if keyword:
            gallery_list = gallery_list.filter(name__istartswith=keyword)
        item_list = gallery_list
        title="Gallery"
    if key == 'job':
        job_list = Job.objects.all()
        ngos_list = NGO.objects.filter(active=True)
        #ngo_obj = Job.objects.filter(ngo=request.GET.get('ngo'))
        status_name = request.GET.get('status_name')
        keyword=request.GET.get('keyword')
        ngo_id = request.GET.get('ngo_name')
        if status_name == "True":
            job_list = job_list.filter(is_active=True)
        if status_name == "False":
            job_list = job_list.filter(is_active=False)
        if keyword:
            job_list = job_list.filter(title__istartswith=keyword)
        if ngo_id:
            job_list = job_list.filter(ngo__id=ngo_id)
        item_list = job_list
        title ="Jobs"
    if key == 'need':
        status_name = request.GET.get('status_name')
        keyword=request.GET.get('keyword')
        ngo_id = request.GET.get('ngo_name')
        need_list = Need.objects.all()
        if status_name == "True":
            need_list = need_list.filter(active=True)
        if status_name == "False":
            need_list = need_list.filter(active=False)
        if keyword:
            need_list = need_list.filter(title__istartswith=keyword)
        if ngo_id:
            need_list = need_list.filter(ngo__id=ngo_id)
        ngos_list = NGO.objects.filter(active=True)
        item_list = need_list
        title = "Needs"
    if key =="home-banner":
        hm_list = HomeBanner.objects.all()
        item_list = hm_list
        title = 'Home Banner'
        status_name = request.GET.get('status_name')
        if status_name == "True":
            item_list = item_list.filter(active=True)
        if status_name == "False":
            item_list = item_list.filter(active=False)
    if key =='volunteer':
        ngos_list = NGO.objects.all().order_by('name')
        volunteer_list = Volunteer.objects.all()
        status_name = request.GET.get('status_name')
        keyword=request.GET.get('keyword')
        if status_name == "True":
            volunteer_list = volunteer_list.filter(active=True)
        if status_name == "False":
            volunteer_list = volunteer_list.filter(active=False)
        if keyword:
            volunteer_list = volunteer_list.filter(name__istartswith=keyword)
        item_list = volunteer_list
        title="Volunteer Requirement"
    if key == "manage-gallery":
        gal_id = request.GET.get('gal_id')
        get_gallery = Gallery.objects.get(id = gal_id)
        image_list = Image.objects.filter(content_type=ContentType.objects.get(model__iexact = 'gallery'),object_id=get_gallery.id)
    if key == 'staff-type':
        staff_list = Staff_Type.objects.all()
        status_name = request.GET.get('status_name')
        keyword=request.GET.get('keyword')
        if status_name == "True":
            staff_list = staff_list.filter(active=True)
        if status_name == "False":
            staff_list = staff_list.filter(active=False)
        if keyword:
            staff_list = staff_list.filter(name__istartswith=keyword)
        item_list = staff_list
        title = 'Staff Type'
    if key == 'staff':
        staff_list = Staff.objects.all()
        status_name = request.GET.get('status_name')
        keyword=request.GET.get('keyword')
        if status_name == "True":
            staff_list = staff_list.filter(active=True)
        if status_name == "False":
            staff_list = staff_list.filter(active=False)
        if keyword:
            staff_list = staff_list.filter(name__icontains=keyword)
        item_list = staff_list
        title = 'Staff'
    if key == 'news':
        news_list = News.objects.all()
        status_name = request.GET.get('status_name')
        keyword=request.GET.get('keyword')
        if status_name == "True":
            news_list = news_list.filter(active=True)
        if status_name == "False":
            news_list = news_list.filter(active=False)
        if keyword:
            news_list = news_list.filter(name__icontains=keyword)
        title = 'News'
    if key == 'hotels':
        hotels_list = Contributing_Hotels.objects.all()
        status_name = request.GET.get('status_name')
        if status_name == "True":
            hotels_list = hotels_list.filter(active=True)
        if status_name == "False":
            hotels_list = hotels_list.filter(active=False)
        title = 'Hotels'
    if key == 'corporate-tables':
        corporate_tables_list = Corporate_Tables.objects.all()
        status_name = request.GET.get('status_name')
        if status_name == "True":
            corporate_tables_list = corporate_tables_list.filter(active=True)
        if status_name == "False":
            corporate_tables_list = corporate_tables_list.filter(active=False)
        title = 'Corporate Tables'
    if key == "fundraisers":
        ngos_list = NGO.objects.filter(active=True).order_by('name')
        fundraisers = Fundraiser.objects.all()
        funds_list = Fundraiser.objects.filter(active=True)
        ulist = list(set(funds_list.values_list('created_by__id',flat = True)))
        flist = User.objects.filter(id__in = ulist).distinct().order_by('first_name')
        year = request.GET.get('year')
        ngo_id = request.GET.get('ngo_name')
        status_name = request.GET.get('status_name')
        keyword=request.GET.get('keyword')
        fname=request.GET.get('fname')
        atype=request.GET.get('atype')
        if atype:
            fundraisers = fundraisers.filter(atype=atype)
        if ngo_id :
            fundraisers = fundraisers.filter(ngo__id=ngo_id)
        if status_name == "True":
            fundraisers = fundraisers.filter(active=True)
        if status_name == "False":
            fundraisers = fundraisers.filter(active=False)
        if keyword:
            if len(keyword) <= 2:
                fundraisers = fundraisers.filter(Q(created_by__first_name__istartswith=keyword) | Q(created_by__last_name__istartswith=keyword))
            else:
                fundraisers = fundraisers.filter(Q(created_by__first_name__icontains=keyword) | Q(created_by__last_name__icontains=keyword))
        if fname:
            fundraisers = fundraisers.filter(created_by__first_name__icontains=fname) or fundraisers.filter(created_by__last_name__icontains=fname)
        item_list = fundraisers
        title = "Fundraiser"
    if key == 'fundraisertype':
        fundraiser_type_list = FundraiserType.objects.all()
        status_name = request.GET.get('status_name')
        if status_name == "True":
            fundraiser_type_list = fundraiser_type_list.filter(active=True)
        if status_name == "False":
            fundraiser_type_list = fundraiser_type_list.filter(active=False)
        item_list = fundraiser_type_list
        title = 'Fundraiser Type'
    if key == 'manage-fundraisertype':
        ftype_id = request.GET.get('ftype_id')
        ftype_obj = FundraiserType.objects.get(id=ftype_id)

    if key == 'projects':
        project_list = Project.objects.all()
        cause_list = Cause.objects.all()
        ngo_list = NGO.objects.filter(active=2)
        item_list = project_list
        title = "Project"
        cause_id = request.GET.get('cause_name', '')
        status_name = request.GET.get('status_name')
        ngo_name = request.GET.get('ngo_name')
        if cause_id:
            item_list = item_list.filter(cause__id=cause_id)
        if status_name == "True":
            item_list = item_list.filter(active=True)
        if status_name == "False":
            item_list = item_list.filter(active=False)
        if ngo_name:
            ngo = ngo_list.get(id=ngo_name)
            item_list = item_list.filter(content_type=ContentType.objects.get(model__iexact='ngo'), object_id=ngo.id)
    if key == 'manage-project':
        project_id = request.GET.get('project_id')
        get_proj = Project.objects.get(id=project_id)

    if key == 'event':
        event_list = Event.objects.all()
        status_name = request.GET.get('status_name')
        if status_name == "True":
            event_list = event_list.filter(active=True)
        if status_name == "False":
            event_list = event_list.filter(active=False)
        item_list = event_list
        title = 'Event'

    if key == "manage-event":
        event_id = request.GET.get('event_id')
        get_event = Event.objects.get(id=event_id)
        event_article_list = EventArticle.objects.filter(content_type=ContentType.objects.get(model__iexact = 'event'), object_id=get_event.id).exclude(slug='overview')
        try:
            event_about_us = EventAboutUs.objects.get(event=get_event)
        except:
            pass
        try:
            event_contact_us = EventContactUs.objects.get(event=get_event)
        except:
            pass
        try:
            event_overview = EventArticle.objects.get(content_type=ContentType.objects.get(model__iexact = 'event'), object_id=get_event.id, slug="overview")
        except:
            pass
        duplicate_corporates_list = Duplicate_Corporates.objects.filter(active=True)

    if key == 'user':
        user_list = User.objects.all()
        name = request.GET.get('name')
        email = request.GET.get('email')
        item_list = user_list
        title = 'User'
        status_name = request.GET.get('status_name')
        if status_name == "True":
            item_list = item_list.filter(is_active=True)
        if status_name == "False":
            item_list = item_list.filter(is_active=False)
        if name:
            if len(name)<= 2:
                item_list = item_list.filter(first_name__istartswith=name) or item_list.filter(last_name__istartswith=name)
            else:
                item_list = item_list.filter(first_name__icontains=name) or item_list.filter(last_name__icontains=name)
        if email:
            item_list = item_list.filter(email__icontains=email)
    if key == 'userprofile':
        userprofile_list = UserProfile.objects.all()
        status_name = request.GET.get('status_name')
        keyword=request.GET.get('keyword')
        if status_name == "True":
            userprofile_list = userprofile_list.filter(active=True)
        if status_name == "False":
            userprofile_list = userprofile_list.filter(active=False)
        if keyword:
            userprofile_list = userprofile_list.filter(user__username__istartswith=keyword)
        item_list = userprofile_list
        title = 'User Profile'
    if key == 'userprofile-reports':
        userprofile_list = UserProfile.objects.all()
        status_name = request.GET.get('status_name')
        keyword=request.GET.get('keyword')
        usertype=request.GET.get('usertype')
        export = request.GET.get('export')
        if status_name == "True":
            userprofile_list = userprofile_list.filter(active=True)
        if status_name == "False":
            userprofile_list = userprofile_list.filter(active=False)
        if keyword:
            userprofile_list = userprofile_list.filter(user__username__istartswith=keyword)
        if usertype:
            userprofile_list = userprofile_list.filter(usertype=usertype)
        if export == "true":
            address = ''
            address1 = ''
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="userprofile_reports_'+str(datetime.now().date())+'.csv"'
            writer = csv.writer(response)
            writer.writerow([ 'Title','First Name', 'Last Name','Gmail','Address1','Address2','City','State','Country','Pincode', 'Mobile'])
            for obj in userprofile_list:
                try:
                    address = Address.objects.get(content_type= ContentType.objects.get(model__iexact='user'), object_id=obj.id)
                except:
                    pass
                try:
                    address = Address.objects.get(content_type=ContentType.objects.get(model__iexact='ngo'), object_id=obj.id)
                except:
                    pass
                writer.writerow([ smart_str(obj.title), smart_str(obj.user.first_name), smart_str(obj.user.last_name), smart_str(obj.user.email),
                                 smart_str(address.address1), smart_str(address.address2), smart_str(address.city), smart_str(address.state), smart_str(address.country),
                                 smart_str(address.pincode), smart_str(address.mobile)
                                ])
            return response
        item_list = userprofile_list
        title = 'User Profile Reports'

    if key == 'ngo-reports':
        ngos_list = NGO.objects.all().order_by('name')
        cause_list = Cause.objects.filter(active=True).order_by('name')
        event_list = Event.objects.filter(active=True).order_by('name')
        select_cause = request.GET.get('cause_name')
        status_name = request.GET.get('status_name')
        event_id = request.GET.get('event')
        ngo_name = request.GET.get('name')
        export = request.GET.get('export')
        choice = request.GET.get('choice')
        devent = request.GET.get('devent')
        ngo_id = request.GET.get('ngo_id')
        if event_id:
            ev=event_list.get(id=event_id)
            ngos_list = ev.ngo.filter(active=True)
        if status_name == "Active":
            ngos_list = ngos_list.filter(active=True)
        if status_name == "Inactive":
            ngos_list = ngos_list.filter(active=False)
        if select_cause:
            cause_obj = cause_list.get(id=select_cause)
            ngos_list=ngos_list.filter(cause__id=select_cause)
        if ngo_name:
            ngos_list = ngos_list.filter(name__icontains=ngo_name)
        if export == "true":
            address = ''
            address1 = ''
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="ngo_reports_'+str(datetime.now().date())+'.csv"'
            writer = csv.writer(response)
            writer.writerow([ 'Name','Established On', 'Registration No','Title','First Name', 'Last Name','Gmail','Address1','Address2','City',
             'State', 'Country', 'Pincode', 'Mobile','cause', 
             'Youtube Embed Link', 'Fund util Stmt', 'Our Mission', 'Work Achivement',
             'FCRA', 'FCRA date', 'FCRA text', 'A12', 'Validity 80G', 'Validity 80G date',
             'Validity 35AC', 'Validity 35AC date', 'Size'
            ])
            for obj in ngos_list:
                try:
                    address = Address.objects.get(content_type=ContentType.objects.get(model__iexact='ngo'), object_id=obj.id)
                except:
                    pass
                writer.writerow([ smart_str(obj.name), smart_str(obj.established_on), smart_str(obj.reg_no), smart_str(obj.contact_person.title), smart_str(obj.contact_person.user.first_name),
                                smart_str(obj.contact_person.user.last_name), smart_str(obj.contact_person.user.email),
                                smart_str(address.address1),smart_str(address.address2),smart_str(address.city),smart_str(address.state),smart_str(address.country),
                                smart_str(address.pincode), smart_str(address.mobile), smart_str(obj.cause),
                                smart_str(obj.youtube_embedd), smart_str(obj.fund_utilisation_statement), smart_str(obj.our_mission), smart_str(obj.work_acheivement),
                                obj.fcra, obj.fcra_date, obj.fcra_text, obj.a12, obj.validity_80G, obj.validity_80G_date,
                                obj.validity_35AC, obj.validity_35AC_date, obj.size
                                ])
            return response
        event_obj = ''
        ngoobj = ''
        if choice == "true":
            if devent:
                event_obj = Event.objects.get(slug=devent)
                ngoobj = NGO.objects.get(id=int(ngo_id))
                online_donations = event_ngo_online_donations(event_obj.id, ngo_id)
                offline_donations = event_ngo_offline_donations(event_obj.id, ngo_id)
                # online donations starts#
                excelstr = '<b>Online Donations (Success)</b>'+'<br>'
                excelstr = excelstr+'<b>NGO Name: '+smart_str(ngoobj.name)+'</b>'+'<br>'
                excelstr = excelstr+'<b>Event name: '+smart_str(event_obj.name)+'</b>'+'<br>'
                excelstr = excelstr+'<table  width="1000"><tr><td></td></tr><tr><th align="left">Donor Name</th><th align="left">Donors email id</th><th align="left">Donation Amount</th><th align="left">PAN Number</th><th align="left">City</th><th align="left">Country</th><th align="left">Transaction NO</th><th align="left">Transaction Date</th><th align="left">Appeal Type</th><th align="left">Fundraiser Name</th>'
                online_donation_amount = 0.0
                for i in online_donations:
                    online_donation_amount = float(online_donation_amount) + float(i.amount)
                    name = i.title+' '+ str(i.first_name)+' ' + str(i.last_name)
                    email = i.email
                    if i.fundraiser:
                        fname = i.fundraiser.created_by.first_name +' ' +i.fundraiser.created_by.last_name
                        ftype = i.fundraiser.fundraiser_type.name
                    else:
                        fname = ""
                        ftype = ''
                    excelstr = excelstr + '<tr><td  align="left" >%s</td><td  align="left">%s</td><td  align="left">%s</td><td  align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td></tr>' %(smart_str(name),smart_str(i.email),smart_str(i.amount), smart_str(i.pan_card), smart_str(i.city),'India',smart_str(i.transaction),smart_str(i.paid_on),smart_str(ftype),smart_str(fname))
                sevn = float(online_donation_amount) * 0.07
                total_disburse = float(online_donation_amount) - float(sevn)
                excelstr = excelstr + '<tr></tr><tr><td></td><td colspan="2"><b>Total: '+smart_str(online_donation_amount)+'</b></td></tr><tr><td></td><td colspan="2"><b>7% of donations: '+smart_str(sevn)+'</b></td></tr><tr><td></td><td colspan="2"><b>Amount to be Disbursed: '+smart_str(total_disburse)+'</b></td></tr></table>'
                # online donations ends#
                if offline_donations:
                    # offline donations starts#
                    excelstr = excelstr+'<br><br>'
                    excelstr = excelstr+'<b>Offline Donations Added</b>'+'<br>'

                    excelstr = excelstr+'<table  width="1000"><tr><td></td></tr><tr><th align="left">Donor Name</th><th align="left">Donors email id</th><th align="left">Donation Amount</th><th align="left">Transaction Date</th><th align="left">Payment Mode</th><th align="left">Payment Details</th><th align="left">Appeal Type</th><th align="left">Fundraiser Name</th><th align="left">PAN Number</th>'
                    offline_donation_amount = 0.0
                    for i in offline_donations:
                        offline_donation_amount = float(offline_donation_amount) + float(i.amount)
                        fname = i.fundraiser.created_by.first_name +' ' +i.fundraiser.created_by.last_name
                        pay_detail = i.cheque_no + ' , ' +i.bank_name
                        excelstr = excelstr + '<tr><td  align="left" >%s</td><td  align="left">%s</td><td  align="left">%s</td><td  align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td></tr>' %(smart_str(i.donor_name),smart_str(i.email),smart_str(i.amount),smart_str(i.date),smart_str(i.payment_mode),smart_str(pay_detail),smart_str(i.fundraiser.fundraiser_type.name),smart_str(fname), smart_str(i.pan_card))
                    excelstr = excelstr + '<tr></tr><tr><td></td><td colspan="2"><b>Total offline: '+smart_str(offline_donation_amount)+'</b></td></tr></table>'
                    # offline donations ends#
            file_name = ''
            if event_obj and ngoobj:
                file_name = smart_str(ngoobj.name) +' - '+ smart_str(event_obj.name)
            else:
                file_name = "NGO Donation reports"
            return write_excel(excelstr,file_name)
        item_list = ngos_list
        title = 'NGO Reports'
    if key == "fundraisers-reports":
        ngos_list = NGO.objects.filter(active=True).order_by('name')
        fundraisers = Fundraiser.objects.all()
        funds_list = Fundraiser.objects.filter(active=True)
        ulist = list(set(funds_list.values_list('created_by__id',flat = True)))
        flist = User.objects.filter(id__in = ulist).distinct()
        year = request.GET.get('year')
        ngo_id = request.GET.get('ngo_name')
        status_name = request.GET.get('status_name')
        keyword=request.GET.get('keyword')
        fname=request.GET.get('fname')
        atype=request.GET.get('atype')
        fids = request.GET.get('fids')
        export = request.GET.get('export')
        export_donations = request.GET.get('export-donations')
        fund_id = request.GET.get('fund_id')
        if fids:
            fids = fids.split(',')
        if atype:
            fundraisers = fundraisers.filter(atype=atype)
        if ngo_id :
            ngo_obj = ngos_list.get(id=ngo_id)
            fundraisers = fundraisers.filter(ngo__id=ngo_id)
        if status_name == "Active":
            fundraisers = fundraisers.filter(active=True)
        if status_name == "Inactive":
            fundraisers = fundraisers.filter(active=False)
        if keyword:
            fundraisers = fundraisers.filter(title__icontains=keyword)
        if fname:
            fundraisers = fundraisers.filter(created_by__first_name__icontains=fname) or fundraisers.filter(created_by__last_name__icontains=fname)
        if export == "true":
            address = ''
            address1 = ''
            excelstr = '<b>Fundraisers</b>'+'<br>'
            excelstr = excelstr+'<table  width="1000"><tr><td></td></tr><tr><th align="left">Title</th><th align="left">Type</th><th align="left">First Name</th><th align="left">Last Name</th><th align="left">Email</th><th align="left">Description</th><th align="left">Thank Msg</th><th align="left">Goal Amount</th>'
            for obj in fundraisers:
                try:
                    address = Address.objects.get(content_type=ContentType.objects.get(model__iexact='user'), object_id=obj.created_by.id)
                except:
                    pass
                excelstr = excelstr + '<tr><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td></tr>' %(smart_str(obj.title), smart_str(obj.fundraiser_type), smart_str(obj.created_by.first_name), smart_str(obj.created_by.last_name), smart_str(obj.created_by.email), smart_str(obj.description), smart_str(obj.thank_msg), smart_str(obj.goal_amount))
            file_name = 'fundraiser_reports_'+str(datetime.now().date())
            return write_excel(excelstr,file_name)
        if export_donations == "true":
            fundraiser = ''
            file_name = ''
            try:
                fundraiser = Fundraiser.objects.get(id=fund_id)
            except:
                pass
            if fundraiser:
                fname = fundraiser.created_by.first_name + ' ' + fundraiser.created_by.last_name
                # online donations starts#
                excelstr = '<b>Online Donations (Success)</b>'+'<br>'
                excelstr = excelstr+'<b>Fundraiser Name: '+fname+'</b>'+'<br>'
                excelstr = excelstr+'<table  width="1000"><tr><td></td></tr><tr><th align="left">Donor Name</th><th align="left">Donors email id</th><th align="left">Donation Amount</th><th align="left">City</th><th align="left">Country</th><th align="left">Transaction NO</th><th align="left">Transaction Date</th><th align="left">PAN Number</th>'
                online_donation_amount = 0.0
                for i in fundraiser.get_donations():
                    online_donation_amount = float(online_donation_amount) + float(i.amount)
                    name = i.title+' '+ str(i.first_name)+' ' + str(i.last_name)
                    excelstr = excelstr + '<tr><td  align="left" >%s</td><td  align="left">%s</td><td  align="left">%s</td><td  align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td></tr>' %(smart_str(name),smart_str(i.email),smart_str(i.amount),smart_str(i.city),'India',smart_str(i.transaction),smart_str(i.paid_on),smart_str(i.pan_card))
                sevn = float(online_donation_amount) * 0.07
                total_disburse = float(online_donation_amount) - float(sevn)
                excelstr = excelstr + '<tr></tr><tr><td></td><td colspan="2"><b>Total: '+smart_str(online_donation_amount)+'</b></td></tr><tr><td></td><td colspan="2"><b>7% of donations: '+smart_str(sevn)+'</b></td></tr><tr><td></td><td colspan="2"><b>Amount to be Disbursed: '+smart_str(total_disburse)+'</b></td></tr></table>'
                # online donations ends#
                if fundraiser.get_offline_donations():
                    # offline donations starts#
                    excelstr = excelstr+'<br><br>'
                    excelstr = excelstr+'<b>Offline Donations Added</b>'+'<br>'

                    excelstr = excelstr+'<table  width="1000"><tr><td></td></tr><tr><th align="left">Donor Name</th><th align="left">Donors email id</th><th align="left">Donation Amount</th><th align="left">Transaction Date</th><th align="left">Payment Mode</th><th align="left">Payment Details</th><th align="left">PAN Number</th>'
                    offline_donation_amount = 0.0
                    for i in fundraiser.get_offline_donations():
                        offline_donation_amount = float(offline_donation_amount) + float(i.amount)
                        fname = fundraiser.created_by.first_name +' ' +fundraiser.created_by.last_name
                        pay_detail = i.cheque_no + ' , ' +i.bank_name
                        excelstr = excelstr + '<tr><td  align="left" >%s</td><td  align="left">%s</td><td  align="left">%s</td><td  align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td></tr>' %(smart_str(i.donor_name),smart_str(i.email),smart_str(i.amount),smart_str(i.date),smart_str(i.payment_mode),smart_str(pay_detail),smart_str(i.pan_card))
                    excelstr = excelstr + '<tr></tr><tr><td></td><td colspan="2"><b>Total offline: '+smart_str(offline_donation_amount)+'</b></td></tr></table>'
                    # offline donations ends#
                file_name = smart_str(fname)
            return write_excel(excelstr,file_name)
        item_list = fundraisers
        title = "Fundraiser Reports"
    if key == "donation-reports":
        total = 0
        donation_list = Donation.objects.all().order_by('-id')
        ngos = NGO.objects.filter(active=True).order_by('name')
        event_list = Event.objects.filter(active=True).order_by('name')
        fundraisers = Fundraiser.objects.filter(active=True).order_by('created_by__first_name')
        startDate = request.GET.get('start_date')
        endDate = request.GET.get('end_date')
        ngo = request.GET.get('ngo')
        fundraiser = request.GET.get('fundraiser')
        event = request.GET.get('event')
        status = request.GET.get('status')
        amount = request.GET.get('amount')
        if ngo:
            ngo_obj = ngos.get(id=ngo)
            donation_list = donation_list.filter(ngo=ngo)
        if event:
            event_obj = event_list.get(id=event)
            donation_list = donation_list.filter(event=event_obj)
        if fundraiser:
            fund_obj = fundraisers.get(id=fundraiser)
            donation_list = donation_list.filter(fundraiser=fund_obj)
        if startDate and endDate:
            donation_list = donation_list.filter(created_on__gte=startDate, created_on__lte=endDate)
        if status:
            donation_list = donation_list.filter(payment_status=status)
        if amount =='1000':
            donation_list = donation_list.filter(amount__lte =amount)
        if amount =='5000':
            donation_list = donation_list.filter(amount__gt =1000,amount__lte=5000)
        if amount =='10000':
            donation_list = donation_list.filter(amount__gt =5000,amount__lte=10000)
        if amount =='50000':
            donation_list = donation_list.filter(amount__gt=10000 ,amount__lte=50000)
        if amount =='50001':
            donation_list = donation_list.filter(amount__gt= 50000 )
        export = request.GET.get('export')
        if export == "true":
            donation_list = donation_list.filter(payment_status="Success")
            excelstr = '<b>Online Donations (Success)</b>'+'<br>'
            excelstr = excelstr+'<table  width="1000"><tr><td></td></tr><tr><th align="left">First Name</th><th align="left">Last Name</th><th align="left">Email</th><th align="left">Address1</th><th align="left">Address2</th><th align="left">City</th><th align="left">State</th><th align="left">Country</th><th align="left">Mobile</th><th align="left">Pan Number</th><th align="left">Amount</th><th align="left">Transaction Id</th><th align="left">Status</th><th align="left">Receipt No</th><th align="left">Date</th><th align="left">NGO</th><th align="left">Fundraiser</th><th align="left">Event</th>'
            for obj in donation_list:
                name = ''
                if obj.fundraiser:
                    name = obj.fundraiser.created_by.first_name + ' ' + obj.fundraiser.created_by.last_name
                excelstr = excelstr + '<tr><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td></tr>' %(smart_str(obj.first_name), smart_str(obj.last_name), smart_str(obj.email), smart_str(obj.address1), smart_str(obj.address2), smart_str(obj.city), smart_str(obj.state), smart_str(obj.country), smart_str(obj.mobile), smart_str(obj.pan_card), smart_str(obj.amount), smart_str(obj.transaction), smart_str(obj.payment_status), smart_str(obj.reciept_no), smart_str(obj.created_on), smart_str(obj.ngo.name) if obj.ngo else None, smart_str(name) if obj.fundraiser else None, smart_str(obj.event.name) if obj.event else None)
            file_name = 'donation_reports_'+str(datetime.now().date())
            return write_excel(excelstr,file_name)
        for i in donation_list:
            if i.payment_status == "Success":
                total=total+i.amount
        item_list = donation_list
        title = "Donation Reports"

    if key == "offline-donation-reports":
        total = 0
        donation_list = Offline_Donation.objects.all().order_by('-id')
        ngos = NGO.objects.filter(active=True).order_by('name')
        event_list = Event.objects.filter(active=True).order_by('name')
        fundraisers = Fundraiser.objects.filter(active=True).order_by('created_by__first_name')
        startDate = request.GET.get('start_date')
        endDate = request.GET.get('end_date')
        ngo = request.GET.get('ngo')
        fundraiser = request.GET.get('fundraiser')
        event = request.GET.get('event')
        amount = request.GET.get('amount')
        if ngo:
            ngo_obj = ngos.get(id=ngo)
            donation_list = donation_list.filter(fundraiser__ngo=ngo)
        if event:
            event_obj = event_list.get(id=event)
            donation_list = donation_list.filter(event=event_obj)
        if fundraiser:
            fund_obj = fundraisers.get(id=fundraiser)
            donation_list = donation_list.filter(fundraiser=fund_obj)
        if startDate and endDate:
            donation_list = donation_list.filter(created_on__gte=startDate, created_on__lte=endDate)
        if amount =='1000':
            donation_list = donation_list.filter(amount__lte =amount)
        if amount =='5000':
            donation_list = donation_list.filter(amount__gt =1000,amount__lte=5000)
        if amount =='10000':
            donation_list = donation_list.filter(amount__gt =5000,amount__lte=10000)
        if amount =='50000':
            donation_list = donation_list.filter(amount__gt=10000 ,amount__lte=50000)
        if amount =='50001':
            donation_list = donation_list.filter(amount__gt= 50000 )
        export = request.GET.get('export')
        for i in donation_list:
            total=total+i.amount
        if export == "true":
            excelstr = '<b>Offline Donations</b>'+'<br>'
            excelstr = excelstr+'<table  width="1000"><tr><td></td></tr><tr><th align="left">Donor Name</th><th align="left">Email</th><th align="left">Address1</th><th align="left">Address2</th><th align="left">Mobile</th><th align="left">Payment Type</th><th align="left">Amount</th><th align="left">Cheque Number</th><th align="left">Bank Name</th><th align="left">Date</th><th align="left">PAN Number</th><th align="left">NGO</th><th align="left">Fundraiser</th><th align="left">Event</th>'
            for obj in donation_list:
                name = ''
                if obj.fundraiser:
                    name = obj.fundraiser.created_by.first_name + ' ' + obj.fundraiser.created_by.last_name
                excelstr = excelstr + '<tr><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td></tr>' %(smart_str(obj.donor_name), smart_str(obj.email), smart_str(obj.address1), smart_str(obj.address2), smart_str(obj.mobile), smart_str(obj.payment_mode), smart_str(obj.amount), smart_str(obj.cheque_no), smart_str(obj.bank_name), smart_str(obj.created_on), smart_str(obj.pan_card), smart_str(obj.fundraiser.ngo.name) if obj.fundraiser else None, smart_str(name) if obj.fundraiser else None, smart_str(obj.event.name) if obj.event else None)
            excelstr = excelstr + '<tr></tr><tr><td align="left" ><b>Total</b></td><td align="left" ><b>%s</b></td></tr>' %(smart_str(total))
            file_name = 'offline_donation_reports_'+str(datetime.now().date())
            return write_excel(excelstr,file_name)
        item_list = donation_list
        title = "Offline Donation Reports"

    if key == "event-donation-reports":
        item_list = Event.objects.filter(active=True).exclude(event_type='Others')
        export = request.GET.get('export')
        devent = request.GET.get('event')
        if export == "True":
            if devent:
                event_obj = Event.objects.get(slug=devent)
                excelstr = '<b>'+ event_obj.name + 'Donations Report</b>'+'<br>'
                excelstr = excelstr+'<table  width="1000"><tr><td></td></tr><tr><th align="left">Name Of the NGO</th><th align="left">Online Donations</th><th align="left">less 7%</th><th align="left">Offline Donations</th><th align="left">TOTAL(Online+Offline)</th><th align="left">No of Fundraisers</th>'
                total_online_donation = 0
                total_offline_donation = 0
                total_sevn = 0.0
                for ngo in event_obj.ngo.all():
                    online_donation = get_event_ngo_online_donations(event_obj.id, ngo.id)
                    sevn = float(online_donation) * 0.07
                    offline_donation = get_event_ngo_offline_donations(event_obj.id, ngo.id)
                    total_donation = ((float(online_donation) - sevn)+float(offline_donation))
                    total_online_donation = total_online_donation + online_donation
                    total_sevn = sevn + total_sevn
                    total_offline_donation = total_offline_donation + offline_donation
                    total = ((float(total_online_donation) - total_sevn)+float(total_offline_donation))
                    nname= (ngo.name).encode('utf-8')
                    excelstr = excelstr + '<tr><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td></tr>' %(smart_unicode(nname), smart_unicode(online_donation), smart_unicode(sevn), smart_unicode(offline_donation), smart_unicode(total_donation), smart_unicode(ngo.get_fundraisers().count()))
                excelstr = excelstr + '<tr></tr>'
                excelstr = excelstr + '<tr><td align="left" >Total</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td><td align="left" >%s</td></tr>' %(str(total_online_donation).encode('utf-8'), str(total_sevn).encode('utf-8'), str(total_offline_donation).encode('utf-8'), str(total).encode('utf-8'))
            file_name = event_obj.name + '_NGO_Wise_reports_'+str(datetime.now().date())
            return write_excel(excelstr,file_name)
        title = "Offline Donation Reports"

    if key =="contact-us":
        contact_list = Contactus.objects.all()
        item_list = contact_list
        title = 'Contact Us'

    if key == "manage-contactus":
        contactus_id = request.GET.get('contactus_id')
        contactus_obj = Contactus.objects.get(id=contactus_id)

    #item_list = pagination(request, item_list)
    return render_to_response('manage/manage.html', locals(), context_instance=RequestContext(request))

# -------------------------------- User --------------------------------------- ---------------- #

def add_user(request):
    if request.method == "POST":
        title = ''
        form = UserInfoForm1(request.POST)
        check =''
        if form.is_valid():
            title_id = request.POST.get('title')
            try:
                title = Salutations.objects.get(id=title_id)
            except:
                pass
            fname = request.POST.get('firstname')
            lname = request.POST.get('lastname')
            pwd = request.POST.get('password1')
            ad1 = request.POST.get('address1')
            ad2 = request.POST.get('address2')
            email = request.POST.get('email')
            city = request.POST.get('city')
            pincode = request.POST.get('pincode')
            state = request.POST.get('state')
            country = request.POST.get('country')
            countryobj = ''
            try:
                country_obj = Country.objects.get(name=country)
            except:
                country_obj = Country.objects.create(name=country)
            try:
                state_obj = State.objects.get(name=state,country=country_obj)
            except:
                state_obj = State.objects.create(name=state,country=country_obj)
            try:
                check = User.objects.get(username=email,email=email)
            except:
                pass
            if not check:
                userobj = User.objects.create_user(username=email,email=email,password=pwd)
                userobj.first_name=fname
                userobj.last_name=lname
                #if not is_active:
                    #userobj.is_active = False
                #else:
                userobj.is_active = True
                userobj.save()
                if title:
                    up = UserProfile(user=userobj,title=title)
                else:
                    up = UserProfile(user=userobj)
                #if not is_active:
                    #up.is_active = False
                #else:
                up.is_active = True
                up.save()
                user_details_obj = UserDetails.objects.create(user=userobj, password=pwd, username=email)
                address = Address.objects.create(address1=ad1, address2=ad2, city=city, content_type = ContentType.objects.get(model__iexact='user'), object_id = userobj.id, pincode=pincode, state=state_obj, country=country_obj)
                return render_to_response('manage/user.html', {'added':True}, context_instance=RequestContext(request))
            else:
                msg = "Email already exists"
                form = UserInfoForm1(request.POST, request.FILES)
                return render_to_response('manage/user.html', {'form':form,'msg':msg}, context_instance=RequestContext(request))
        else:
            form = UserInfoForm1(request.POST, request.FILES)
        return render_to_response('manage/user.html', {'form':form}, context_instance=RequestContext(request))
    else:
        form = UserInfoForm1()
    return render_to_response('manage/user.html', {'form':form}, context_instance=RequestContext(request))




def edit_user(request, usr_id=''):
    title=''
    if usr_id == '':
        usr_id = request.GET.get('usr_id')
    usr = UserProfile.objects.get(user__id=usr_id)
    address = ''
    try:
        address = Address.objects.get(content_type = ContentType.objects.get(model__iexact='user'), object_id = usr_id)
    except:
        pass
    try:
        ngo_obj = NGO.objects.get(contact_person__user__id=usr_id)
        address = Address.objects.get(content_type = ContentType.objects.get(model__iexact='ngo'), object_id = ngo_obj.id)
    except:
        pass
    userobj=''
    title = ''
    if request.method== "POST":
        form = UserProfileEditForm(request.POST)
        if form.is_valid():
            fname = request.POST.get('first_name')
            lname = request.POST.get('last_name')
            ad1 = request.POST.get('address1')
            ad2 = request.POST.get('address2')
            city = request.POST.get('city')
            title_id = request.POST.get('title')
            try:
                title = Salutations.objects.get(id=title_id)
            except:
                pass
            pincode = request.POST.get('pincode')
            state = request.POST.get('state')
            country = request.POST.get('country')
            countryobj = ''
            try:
                country_obj = Country.objects.get(name=country)
            except:
                country_obj = Country.objects.create(name=country)
            try:
                state_obj = State.objects.get(name=state,country=country_obj)
            except:
                state_obj = State.objects.create(name=state,country=country_obj)
            userobj = User.objects.get(id=usr.user.id)
            #if not is_active:
                #userobj.is_active=False
            #else:
                #userobj.is_active=True
            userobj.first_name=fname
            userobj.last_name=lname
            userobj.save()
            if title:
                usr.title=title
                usr.save()
            pobj = ''
            try:
                pobj = UserActive.objects.get(user=userobj)
            except:
                pass
            if userobj.is_active == True:
                sub = "Account Details for "+ userobj.first_name + " at Bangalore Cares"
                content = ("Dear "+ userobj.first_name + ",\n\n" + "Thank you for registering at Bangalorecares.in. Your account is activated.you can login to http://bangalorecares.in/ using the following email and password: "+"\n" +"Email: " +userobj.username+"\n"+"\n\nYou can now do the following on your pages:\n\n    a.You can edit the content of your page and update all communication details\n\n    b.Make a donation to any cause of your choice and any number of times, with a donation history available for ready reference\n\n    c.You can volunteer with any organization\n\n    d.You can fulfill the non cash needs of any NGO\n\n    e.You can fundraise for any project of an NGO\n\n" + "For any queries please write to admin@bangalorecares.in\n" + "\n" +"Regards,\n" +"Team Bangalore Cares")
                Sender_mail = "admin@bangalorecares.in"
                reciever_mail = [userobj.email]
                sender = "tcsw10k2013@bangalorecares.in"
                reciever = ['admin@bangalorecares.in',]
                subject = "Account Details for "+ userobj.first_name + " at Bangalore Cares"
                message = "Hello Administrator," +"\n\n"+ "A new user has registered at Bangalorecares.in."+ "\n\n" +"This e-mail contains their details:"+"\n\n"+"Name: "+userobj.first_name+"\n"+"E-mail: "+userobj.email+"\n\n"+"Please do not respond to this message. It is automatically generated and is for information purposes only."
                email = EmailMessage(sub,content, Sender_mail,reciever_mail,headers = {'Reply-To': Sender_mail})
                #email.send()
                email1 = EmailMessage(subject,message, sender,reciever,headers = {'Reply-To': sender})
                #email1.send()
            address.address1=ad1
            address.title=title
            address.address2=ad2
            address.pincode=pincode
            address.state = state_obj
            address.country = country_obj
            address.save()
            return render_to_response('manage/user.html', {'edit_done':True, 'usr_id':usr_id}, context_instance=RequestContext(request))
        else:
            form = UserProfileEditForm(request.POST)
        return render_to_response('manage/user.html', {'form':form, 'edit':True, 'usr_id':usr_id,'address':address}, context_instance=RequestContext(request))
    else:
        form = UserProfileEditForm(initial={'title':usr.title,'first_name':usr.user.first_name,'last_name':usr.user.last_name,'address1':address.address1,
        'address2':address.address2,'city':address.city,'pincode':address.pincode, 'state':address.state, 'country':address.country,
        'username':usr.user.username, 'email':usr.user.email})
    return render_to_response('manage/user.html', {'form':form, 'edit':True, 'usr_id':usr_id,'address':address,'sts':address.state.name,'cnty':address.country}, context_instance=RequestContext(request))

def delete_user(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = User.objects.get(id=id)
    obj.is_active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=user')

def activate_user(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = User.objects.get(id=id)
    obj.is_active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=user')
# -------------------------------- User Profile --------------------------------------- ---------------- #


def add_userprofile(request):
   
    if request.method == "POST":
        form = UserProfileForm7(request.POST)
        if form.is_valid():
            
            user_id = request.POST.get('user')
            user_obj = User.objects.get(id=user_id)
            check=UserProfile.objects.filter(user__username=user_obj.username)
            if not check:
                form.save()
                return render_to_response('manage/add_userprofile.html', {'added':True}, context_instance=RequestContext(request))
            else:
                error= "User name already exist."
                form = UserProfileForm7(request.POST)
                return render_to_response('manage/add_userprofile.html', {'form':form, 'error':error}, context_instance=RequestContext(request))
        else:
            form = UserProfileForm7(request.POST)
        return render_to_response('manage/add_userprofile.html', {'form':form}, context_instance=RequestContext(request))
    else:
        form = UserProfileForm7()
    return render_to_response('manage/add_userprofile.html', {'form':form}, context_instance=RequestContext(request))


def edit_userprofile(request, user_id=''):
    if user_id== '':
        user_id=request.GET.get('user_id', '')
    
    userprofile = UserProfile.objects.get(id=user_id)
    if request.method == "POST":
        form = UserProfileForm7(request.POST, instance = userprofile)
        if form.is_valid():
            if not has_changed(instance= userprofile,field='user'):
                    form.save()
                    return render_to_response('manage/add_userprofile.html', {'edit_done':True, 'user_id':user_id}, context_instance=RequestContext(request))
            else:
                user_id = request.POST.get('user')
                user_obj = User.objects.get(id=user_id)
                check=UserProfile.objects.filter(user__username=user_obj.username).exclude(id = userprofile.id)
                if not check:
                    form.save()
                    return render_to_response('manage/add_userprofile.html', {'edit_done':True, 'user_id':user_id}, context_instance=RequestContext(request))
                else:
                    error= "User name already exist"
                    form = UserProfileForm7(request.POST)
                    return render_to_response('manage/add_userprofile.html', {'form':form, 'edit':True, 'error':error, 'user_id':user_id}, context_instance=RequestContext(request))    
        else:
            form = UserProfileForm7(request.POST)
        return render_to_response('manage/add_userprofile.html', {'form':form, 'edit':True, 'user_id':user_id}, context_instance=RequestContext(request))
    else:
        form = UserProfileForm7(instance= userprofile)
    return render_to_response('manage/add_userprofile.html', {'form':form, 'edit':True, 'user_id':user_id}, context_instance=RequestContext(request))

def delete_userprofile(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = UserProfile.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=userprofile')

def activate_userprofile(request, id=''):
    
    if id == '':
        id = request.GET.get('id')
    obj = UserProfile.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=userprofile')

# -------------------------------- Our Events--------------------------------------- ---------------- #

def add_ourevents(request):
    if request.method == "POST":
        form = OurEventsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            added = True
            return render_to_response('manage/add_edit_ourevents.html', locals(), context_instance=RequestContext(request))
        else:
            form = OurEventsForm(request.POST, request.FILES)
        return render_to_response('manage/add_edit_ourevents.html', locals(), context_instance=RequestContext(request))
    else:
        form = OurEventsForm()
    return render_to_response('manage/add_edit_ourevents.html', locals(), context_instance=RequestContext(request))



def edit_ourevents(request):
    edit = True
    evt_id=request.GET.get('eid')
    event=Our_Events.objects.get(id=evt_id)
    if request.method== "POST":
        form=OurEventsForm(request.POST,instance = event)
        if form.is_valid():
            form.save()
            edit_done = True
        else:
            form=OurEventsForm(request.POST)
            return render_to_response('manage/add_edit_ourevents.html', locals(), context_instance=RequestContext(request))
    else:
        form=OurEventsForm(instance = event)
        return render_to_response('manage/add_edit_ourevents.html', locals(), context_instance=RequestContext(request))
    return render_to_response('manage/add_edit_ourevents.html', locals(), context_instance=RequestContext(request))


def delete_ourevents(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Our_Events.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=ourevents')

def activate_ourevents(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Our_Events.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=ourevents')


# -------------------------------- Home Banner--------------------------------------- ---------------- #

def add_homebanner(request):
    if request.method == "POST":
        form = HomeBannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            added = True
            return render_to_response('manage/add_edit_homebanner.html', locals(), context_instance=RequestContext(request))
        else:
            form = HomeBannerForm(request.POST, request.FILES)
        return render_to_response('manage/add_edit_homebanner.html', locals(), context_instance=RequestContext(request))
    else:
        form = HomeBannerForm()
    return render_to_response('manage/add_edit_homebanner.html', locals(), context_instance=RequestContext(request))



def edit_homebanner(request):
    edit = True
    hm_id=request.GET.get('hm_id')
    homebanner = HomeBanner.objects.get(id=hm_id)
    if request.method== "POST":
        form=HomeBannerForm(request.POST, request.FILES, instance = homebanner)
        if form.is_valid():
            form.save()
            edit_done = True
        else:
            form=HomeBannerForm(request.POST)
            return render_to_response('manage/add_edit_homebanner.html', locals(), context_instance=RequestContext(request))
    else:
        form=HomeBannerForm(instance = homebanner)
        return render_to_response('manage/add_edit_homebanner.html', locals(), context_instance=RequestContext(request))
    return render_to_response('manage/add_edit_homebanner.html', locals(), context_instance=RequestContext(request))


def delete_homebanner(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = HomeBanner.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=home-banner')

def activate_homebanner(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = HomeBanner.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=home-banner')

# -------------------------------- Volunteer--------------------------------------- ---------------- #

def add_volunteer(request):
    count = ''
    warn_msg = ''
    added_volunteer = ''
    if request.method== "POST":
        form1=VolunteerForm(request.POST)
        form2=NeedNgoForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            obj=form1.save(commit=False)
            ngo_id = request.POST.get('ngo')
            if ngo_id:
                ngo = NGO.objects.get(id=ngo_id)
                added_volunteer = Volunteer.objects.filter(is_active=True)
                count = len(added_volunteer)
                if count >=3:
                    warn_msg='You already reached maximum number of Active Volunteer.'
                else:
                    obj.save()
                    ngo.volunteer.add(obj)
                return render_to_response('manage/volunteer.html', {'added':True,'warn_msg':warn_msg,'count':count}, context_instance=RequestContext(request))
        else:
            form1=VolunteerForm(request.POST)
            form2=NeedNgoForm(request.POST)
        return render_to_response('manage/volunteer.html', {'form1':form1,'form2':form2}, context_instance=RequestContext(request))
    else:
        form1=VolunteerForm()
        form2=NeedNgoForm()
    return render_to_response('manage/volunteer.html', {'form1':form1,'form2':form2}, context_instance=RequestContext(request))



def edit_volunteer(request):
    ngolist=''
    count = ''
    warn_msg = ''
    v_id = request.GET.get('v_id')
    v = Volunteer.objects.get(pk=v_id)
    try:
        ngolist=NGO.objects.get(volunteer=v)
    except:
        pass
    if request.method== "POST":
        form1=VolunteerForm(request.POST,instance=v)
        form2=NeedNgoForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            obj=form1.save(commit=False)
            nid = request.POST.get('ngo')
            if ngolist:
                ngolist.volunteer.remove(obj)
            if nid:
                ngo_obj=NGO.objects.get(id=nid)
                count = len(ngo_obj.volunteer.filter(active=True))
                if count >=3:
                    warn_msg='You already reached maximum number of Active Vounteer.'
                else:
                    obj.save()
                    ngo_obj.volunteer.add(obj)
            return render_to_response('manage/volunteer.html', {'edit_done':True,'warn_msg':warn_msg,'count':count}, context_instance=RequestContext(request))
        else:
            form1=VolunteerForm(request.POST)
            form2=NeedNgoForm(request.POST)
        return render_to_response('manage/volunteer.html', {'v':v,'form1':form1, 'form2':form2, 'edit':True}, context_instance=RequestContext(request))
    else:
        form1=VolunteerForm(instance=v)
        form2=NeedNgoForm(initial={'ngo':ngolist})
    return render_to_response('manage/volunteer.html', {'v':v, 'form1':form1,'form2':form2, 'edit':True}, context_instance=RequestContext(request))




def delete_volunteer(request,id=''):
    if  id=='':
        id = request.GET.get('id')
    obj = Volunteer.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=volunteer')
def delete_frontvolunteer(request,id=''):
    if  id=='':
        id = request.GET.get('id')
    obj = Volunteer.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=volunteer')

# -------------------------------- Need--------------------------------------- ---------------- #

def add_need(request):
    count = ''
    added_needs = ''
    ngo_id = ''
    ngo_id = request.GET.get('ngo_id')
    if request.method== "POST":
        form1=NeedForm(request.POST,request.FILES)
        if form1.is_valid():
            if ngo_id:
                ngo = NGO.objects.get(id=ngo_id)
                added_needs = Need.objects.filter(content_type = ContentType.objects.get(model__iexact='ngo'), object_id=ngo.id, active=True)
                count = len(added_needs)
                if count >=3:
                    warn_msg='You already reached maximum number of Active Needs.'
                    return render_to_response('manage/add_need.html',locals(), context_instance=RequestContext(request))
                else:
                    ct = ContentType.objects.get(model__iexact='ngo')
                    need_obj = Need.objects.create(name=request.POST.get('name'), 
                                            description=request.POST.get('description'),
                                            icon=request.FILES.get('icon'),
                                            content_type=ct)
                    need_obj.object_id = ngo.id
                    need_obj.save()
                    added = True
                return render_to_response('manage/add_need.html', locals(), context_instance=RequestContext(request))
        else:
            form1=NeedForm(request.POST,request.FILES)
        return render_to_response('manage/add_need.html', locals(), context_instance=RequestContext(request))
    else:
        form1=NeedForm()
    return render_to_response('manage/add_need.html', locals(), context_instance=RequestContext(request))



def edit_need(request, nd_id =''):
    count = ''
    edit = True
    if nd_id =='':
        nd_id = int(request.GET.get('nd_id'))
    need_obj = Need.objects.get(id=nd_id)
    if request.method== "POST":
        form1=NeedForm(request.POST, request.FILES , instance = need_obj)
        if form1.is_valid():
            form1.save()
            edit_done = True
            return render_to_response('manage/add_need.html', locals(), context_instance=RequestContext(request))
        else:
            form1 = NeedForm(request.POST, request.FILES)
        return render_to_response('manage/add_need.html', locals(), context_instance=RequestContext(request))
    else:
        form1 = NeedForm(instance=need_obj)
    return render_to_response('manage/add_need.html',locals(), context_instance=RequestContext(request))

def delete_need(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Need.objects.get(id=id)
    obj.active = False
    obj.save()
    ngo_id = request.GET.get('ngo_id')
    return HttpResponseRedirect('/manage/?key=manage-ngos&ngo_id='+ngo_id)

def activate_need(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Need.objects.get(id=id)
    obj.active = True
    obj.save()
    ngo_id = request.GET.get('ngo_id')
    return HttpResponseRedirect('/manage/?key=manage-ngos&ngo_id='+ngo_id)

# -------------------------------- Volunteer Requirements--------------------------------------- ---------------- #

def add_volreq(request):
    count = ''
    added_volreq = ''
    ngo_id = ''
    ngo_id = request.GET.get('ngo_id')
    if request.method== "POST":
        form1=VolunteerReqForm(request.POST,request.FILES)
        if form1.is_valid():
            if ngo_id:
                ngo = NGO.objects.get(id=ngo_id)
                added_volreq = Volunteer_Requirements.objects.filter(content_type = ContentType.objects.get(model__iexact='ngo'), object_id=ngo.id, active=True)
                count = len(added_volreq)
                if count >=3:
                    warn_msg='You already reached maximum number of Active Volunteer Requirements.'
                    return render_to_response('manage/add_ngo_volunteer.html',locals(), context_instance=RequestContext(request))
                else:
                    ct = ContentType.objects.get(model__iexact='ngo')
                    volreq_obj = Volunteer_Requirements.objects.create(name=request.POST.get('name'), 
                                            description=request.POST.get('description'),
                                            icon=request.FILES.get('icon'),
                                            content_type=ct)
                    volreq_obj.object_id = ngo.id
                    volreq_obj.save()
                    added = True
                return render_to_response('manage/add_ngo_volunteer.html', locals(), context_instance=RequestContext(request))
        else:
            form1=VolunteerReqForm(request.POST,request.FILES)
        return render_to_response('manage/add_ngo_volunteer.html', locals(), context_instance=RequestContext(request))
    else:
        form1=VolunteerReqForm()
    return render_to_response('manage/add_ngo_volunteer.html', locals(), context_instance=RequestContext(request))

def edit_volreq(request, nd_id =''):
    count = ''
    edit = True
    if nd_id =='':
        nd_id = int(request.GET.get('nd_id'))
    volreq_obj = Volunteer_Requirements.objects.get(id=nd_id)
    if request.method== "POST":
        form1=VolunteerReqForm(request.POST, request.FILES , instance = volreq_obj)
        if form1.is_valid():
            form1.save()
            edit_done = True
            return render_to_response('manage/add_ngo_volunteer.html', locals(), context_instance=RequestContext(request))
        else:
            form1 = VolunteerReqForm(request.POST, request.FILES)
        return render_to_response('manage/add_ngo_volunteer.html', locals(), context_instance=RequestContext(request))
    else:
        form1 = VolunteerReqForm(instance=volreq_obj)
    return render_to_response('manage/add_ngo_volunteer.html',locals(), context_instance=RequestContext(request))

def delete_volreq(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Volunteer_Requirements.objects.get(id=id)
    obj.active = False
    obj.save()
    ngo_id = request.GET.get('ngo_id')
    return HttpResponseRedirect('/manage/?key=manage-ngos&ngo_id='+ngo_id)

def activate_volreq(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Volunteer_Requirements.objects.get(id=id)
    obj.active = True
    obj.save()
    ngo_id = request.GET.get('ngo_id')
    return HttpResponseRedirect('/manage/?key=manage-ngos&ngo_id='+ngo_id)

# -------------------------------- Jobs--------------------------------------- ---------------- #

from datetime import *
def add_job(request):
    count = ''
    warn_msg = ''
    added_jobs = ''
    if request.method== "POST":
        today = date.today()
        form1=JobForm(request.POST,request.FILES)
        form2=NeedNgoForm(request.POST)
        if form1.is_valid():
            title = request.POST.get('title')
            obj = form1.save(commit=False)
            obj.posted_date = today
            obj.url4SEO=slugify(title)
            ngo_id = int(request.POST.get('ngo'))
            ngo = NGO.objects.get(id=ngo_id)
            obj.content_type = ContentType.objects.get(model__iexact='ngo')
            obj.object_id = ngo.id
            obj.save()
                #ngo.jobs.add(obj)
            added = True
            return render_to_response('manage/add_job.html', locals(), context_instance=RequestContext(request))
        else:
            form1=JobForm(request.POST,request.FILES)
            form2=NeedNgoForm(request.POST)
        return render_to_response('manage/add_job.html', locals(), context_instance=RequestContext(request))
    else:
        form1=JobForm()
        form2=NeedNgoForm()
    return render_to_response('manage/add_job.html', locals(), context_instance=RequestContext(request))


def edit_job(request, job_id=''):
    edit = True
    if job_id == '':
        job_id = request.GET.get('job_id')
    job=Job.objects.get(id=job_id)
    if request.method== "POST":
        form1=JobForm(request.POST,request.FILES,instance=job)
        form2=NeedNgoForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            title = request.POST.get('title')
            obj = form1.save(commit=False)
            #obj.posted_date = today
            obj.url4SEO=slugify(title)
            ngo_id = int(request.POST.get('ngo'))
            ngo = NGO.objects.get(id=ngo_id)
            obj.content_type = ContentType.objects.get(model__iexact='ngo')
            obj.object_id = ngo.id
            obj.save()
            edit_done = True
            return render_to_response('manage/add_job.html', locals(), context_instance=RequestContext(request))
        else:
            form1=JobForm(request.POST,request.FILES)
            form2=NeedNgoForm(request.POST)
        return render_to_response('manage/add_job.html', locals(), context_instance=RequestContext(request))
    else:
        form1=JobForm(instance = job)
        form2=NeedNgoForm(initial = {'ngo':job.object_id})
    return render_to_response('manage/add_job.html', locals(), context_instance=RequestContext(request))



def delete_job(request, job_id=''):
    if job_id == '':
        job_id = request.GET.get('job_id')
    obj = Job.objects.get(id=job_id)
    obj.is_active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=job')


def activate_job(request, job_id=''):
    if job_id == '':
        job_id = request.GET.get('job_id')
    obj = Job.objects.get(id=job_id)
    obj.is_active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=job')

# -------------------------------- NGO Cause--------------------------------------- ---------------- #

def add_cause(request):
    if request.method == "POST":
        form = CauseForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save(commit=False)
            f.slug = slugify(request.POST.get('name'))
            f.save()
            return render_to_response('manage/add_cause.html', {'added':True}, context_instance=RequestContext(request))
        else:
            form = CauseForm(request.POST, request.FILES)
        return render_to_response('manage/add_cause.html', {'form':form}, context_instance=RequestContext(request))
    else:
        form = CauseForm()
    return render_to_response('manage/add_cause.html', locals(), context_instance=RequestContext(request))



def edit_cause(request):
    #import ipdb;ipdb.set_trace()
    edit = True
    c_id=request.GET.get('cid')
    cause=Cause.objects.get(id=c_id)
    if request.method== "POST":
        form=CauseForm(request.POST, request.FILES, instance = cause)
        if form.is_valid():
            form.save()
            edit_done = True
        else:
            form=CauseForm(request.POST)
            return render_to_response('manage/add_cause.html', locals(), context_instance=RequestContext(request))
    else:
        form=CauseForm(instance = cause)
        return render_to_response('manage/add_cause.html', locals(), context_instance=RequestContext(request))
    return render_to_response('manage/add_cause.html', locals(), context_instance=RequestContext(request))


def delete_cause(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Cause.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=cause')

def activate_cause(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Cause.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=cause')

'''def add_ads(request):
    if request.method == "POST":
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render_to_response('manage/add_ads.html', {'added':True}, context_instance=RequestContext(request))
        else:
            form = AdvertisementForm(request.POST, request.FILES)
        return render_to_response('manage/add_ads.html', {'form':form}, context_instance=RequestContext(request))
    else:
        form = AdvertisementForm()
    return render_to_response('manage/add_ads.html', {'form':form}, context_instance=RequestContext(request))'''


# --------------------------------  Advertisement --------------------------------------- ---------------- #


def add_ads(request):
    if request.method == "POST":
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render_to_response('manage/add_ads.html', {'added':True}, context_instance=RequestContext(request))
        else:
            form = AdvertisementForm(request.POST, request.FILES)
        return render_to_response('manage/add_ads.html', {'form':form}, context_instance=RequestContext(request))
    else:
        form = AdvertisementForm()
    return render_to_response('manage/add_ads.html', {'form':form}, context_instance=RequestContext(request))


def edit_ads(request, ad_id=''):
    if ad_id== '':
        ad_id=request.GET.get('ad_id', '')
    advert=Ads.objects.get(id=ad_id)
    if request.method == "POST":
        form = AdvertisementForm(request.POST,request.FILES,instance=advert)
        if form.is_valid():
            if not has_changed(instance=advert,field='name'):
                form.save()
                return render_to_response('manage/add_ads.html', {'edit_done':True, 'ad_id':ad_id}, context_instance=RequestContext(request))
            else:
                check=Advertisement.objects.filter(title__iexact=request.POST.get('title'))
                if not check:
                    form.save()
                    return render_to_response('manage/add_ads.html', {'edit_done':True, 'ad_id':ad_id}, context_instance=RequestContext(request))
                else:
                    error= "Advertisement name already exist"
                    form = AdvertisementForm(request.POST)
                return render_to_response('manage/add_ads.html', {'form':form, 'edit':True, 'ad_id':ad_id}, context_instance=RequestContext(request))    
        else:
            form = AdvertisementForm(request.POST)
            return render_to_response('manage/add_ads.html', {'form':form, 'edit':True, 'ad_id':ad_id}, context_instance=RequestContext(request))
    else:
        form = AdvertisementForm(instance=advert)
    return render_to_response('manage/add_ads.html', {'form':form, 'edit':True, 'ad_id':ad_id}, context_instance=RequestContext(request))


def delete_ads(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Ads.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=advertisement')

def activate_ads(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Ads.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=advertisement')

# --------------------------------  Activity --------------------------------------- ---------------- #

def add_activity(request):
    if request.method== "POST":
        form1=ActivityForm(request.POST,request.FILES)
        if form1.is_valid():
            f= form1.save(commit = False)
            f.save()
            return render_to_response('manage/add_activity.html', {'added':True}, context_instance=RequestContext(request))
        else:
            form1=ActivityForm(request.POST,request.FILES)
        return render_to_response('manage/add_activity.html', {'form1':form1}, context_instance=RequestContext(request))
    else:
        form1=ActivityForm()
    return render_to_response('manage/add_activity.html', {'form1':form1}, context_instance=RequestContext(request))


def edit_activity(request, act_id=''):
    if act_id == '':
        act_id=request.GET.get('act_id')
    activity=Activity.objects.get(id=act_id)
    if request.method== "POST":
        form1=ActivityForm(request.POST,request.FILES,instance=activity)
        if form1.is_valid():
            f=form1.save()
            return render_to_response('manage/add_activity.html', {'edit_done':True, 'act_id':act_id}, context_instance=RequestContext(request))
        else:
            form=ActivityForm(request.POST,request.FILES)
        return render_to_response('manage/add_activity.html', {'form1':form1,'edit':True, 'act_id':act_id}, context_instance=RequestContext(request))
    else:
        form1=ActivityForm(instance=activity)
    return render_to_response('manage/add_activity.html', {'form1':form1, 'edit':True, 'act_id':act_id}, context_instance=RequestContext(request))

def delete_activity(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Activity.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=activity')

def activate_activity(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Activity.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=activity')

# --------------------------------  Gallery --------------------------------------- ---------------- #

def add_gallery(request):
    if request.method== "POST":
        form=GalleryForm(request.POST, request.FILES)
        if form.is_valid():    
            check=Gallery.objects.filter(name__iexact=request.POST.get('name'))
            if not check:
                f= form.save(commit=False)
                f.slug = slugify(request.POST.get('name'))
                f.save()
                return render_to_response('manage/add_gallery.html', {'added':True}, context_instance=RequestContext(request))
            else:
                error= "Gallery name already exist."
            return render_to_response('manage/add_gallery.html', locals(), context_instance=RequestContext(request))
        else:
            form = GalleryForm(request.POST, request.FILES)
        return render_to_response('manage/add_gallery.html', locals(), context_instance=RequestContext(request))
    else:
        form = GalleryForm()
    return render_to_response('manage/add_gallery.html', locals(), context_instance=RequestContext(request))

def edit_gallery(request, gal_id=''):
    if gal_id == '':
        gal_id = request.GET.get('gal_id')
    gallery=Gallery.objects.get(id=gal_id)
    if request.method== "POST":
        form=GalleryForm(request.POST,request.FILES,instance=gallery)
        if form.is_valid():
            form.save()
            form = GalleryForm(request.POST, request.FILES)
            return render_to_response('manage/add_gallery.html', {'edit_done':True, 'gal_id':gal_id}, context_instance=RequestContext(request))
        else:
            form = GalleryForm(request.POST, request.FILES)
        return render_to_response('manage/add_gallery.html', {'form':form, 'edit':True, 'gal_id':gal_id}, context_instance=RequestContext(request))
    else:
        form=GalleryForm(instance=gallery)
    return render_to_response('manage/add_gallery.html', {'form':form, 'edit':True, 'gal_id':gal_id}, context_instance=RequestContext(request))

def delete_gallery(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Gallery.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=gallery')


def activate_gallery(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Gallery.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=gallery')


# -------------------------------- Faq Category--------------------------------------- ---------------- #


def add_faq_category(request):
    if request.method == "POST":
        form = FAQ_CategoryForm(request.POST)
        if form.is_valid():
            event_id = request.POST.get('event')
            if event_id:
                event_obj = Event.objects.get(id=event_id)
                check=FAQ_Category.objects.filter(name__iexact=request.POST.get('name'), event=event_obj)
            else:
                check=FAQ_Category.objects.filter(name__iexact=request.POST.get('name'), choice='main')
            if not check:
                f = form.save(commit=False)
                if event_id:
                    f.event = event_obj
                f.save()
                added = True
                return render_to_response('manage/add_faq_category.html', locals(), context_instance=RequestContext(request))
            else:
                error= "Category name already exist."
                form = FAQ_CategoryForm(request.POST)
                return render_to_response('manage/add_faq_category.html', locals(), context_instance=RequestContext(request))
        else:
            form = FAQ_CategoryForm(request.POST)
        return render_to_response('manage/add_faq_category.html', locals(), context_instance=RequestContext(request))
    else:
        form = FAQ_CategoryForm()
    return render_to_response('manage/add_faq_category.html', locals(), context_instance=RequestContext(request))


def edit_faq_category(request, faq_id=''):
    edit = True
    if faq_id== '':
        faq_id=request.GET.get('faq_id', '')
    category=FAQ_Category.objects.get(id=faq_id)
    if request.method == "POST":
        form = FAQ_CategoryForm(request.POST, instance = category)
        if form.is_valid():
            event_id = request.POST.get('event')
            if event_id:
                event_obj = Event.objects.get(id=event_id)
            if not has_changed(instance=category,field='name'):
                    form.save()
                    edit_done =True
                    return render_to_response('manage/add_faq_category.html', locals(), context_instance=RequestContext(request))
            else:
                if event_id:
                    check=FAQ_Category.objects.filter(name__iexact=request.POST.get('name'), event=event_obj)
                else:
                    check=FAQ_Category.objects.filter(name__iexact=request.POST.get('name'), choice='main')
                if not check:
                    form.save()
                    edit_done=True
                    return render_to_response('manage/add_faq_category.html', locals(), context_instance=RequestContext(request))
                else:
                    error= "Category name already exist"
                    form = FAQ_CategoryForm(request.POST)
                    return render_to_response('manage/add_faq_category.html', locals(), context_instance=RequestContext(request))    
        else:
            form = FAQ_CategoryForm(request.POST)
        return render_to_response('manage/add_faq_category.html', locals(), context_instance=RequestContext(request))
    else:
        form = FAQ_CategoryForm(instance=category)
    return render_to_response('manage/add_faq_category.html', locals(), context_instance=RequestContext(request))


def delete_faq_category(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = FAQ_Category.objects.get(id=id)
    obj.is_active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=faq')

def activate_faq_category(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = FAQ_Category.objects.get(id=id)
    obj.is_active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=faq')

# -------------------------------- Question and Answer  --------------------------------------- ---------------- #
def add_question(request,faq_id=''):
    faq_id = request.GET.get('faq_id')
    faq_cat = FAQ_Category.objects.get(id=faq_id)
    if request.method == "POST":
        form = QuestionForm(request.POST)
        form1 = AnswerForm(request.POST)
        if form.is_valid() and form1.is_valid():
                check=Question.objects.filter(question__iexact=request.POST.get('question'), category=faq_cat)
                if not check:
                    f=form.save(commit=False)
                    f.category = faq_cat
                    f.save()
                    f1 = form1.save(commit=False)
                    f1.question = f
                    f1.save()
                    added = True
                    return render_to_response('manage/add_question.html', locals(), context_instance=RequestContext(request))
                else:
                    error= "Question already exist."
                    form = QuestionForm(request.POST)
                    form1 = AnswerForm(request.POST)
                return render_to_response('manage/add_question.html', locals(), context_instance=RequestContext(request))
        else:
            form = QuestionForm(request.POST)
            form1 = AnswerForm(request.POST)
            return render_to_response('manage/add_question.html', locals(), context_instance=RequestContext(request))
    else:
        form = QuestionForm()
        form1 = AnswerForm()
    return render_to_response('manage/add_question.html', locals(), context_instance=RequestContext(request))


def edit_question(request, quest_id=''):
    answer = ''
    edit = True
    if quest_id== '':
        quest_id=request.GET.get('quest_id', '')
    question=Question.objects.get(id=quest_id)
    try:
        answer = Answer.objects.get(question=question)
    except:
        pass
    if request.method == "POST":
        form = QuestionForm(request.POST, instance = question)
        if answer:
            form1 = AnswerForm(request.POST, instance = answer)
        else:
            form1 = AnswerForm(request.POST)
        if form.is_valid() and form1.is_valid():
            f = form.save(commit=False)
            f.save()
            f1 = form1.save(commit=False)
            f1.question = f
            f1.save()
            edit_done = True
            return render_to_response('manage/add_question.html', locals(), context_instance=RequestContext(request))
        else:
            form = QuestionForm(request.POST)
            form1 = AnswerForm(request.POST)
            return render_to_response('manage/add_question.html', locals(), context_instance=RequestContext(request))
    else:
        form = QuestionForm(instance=question)
        if answer:
            form1 = AnswerForm(instance=answer)
        else:
            form1 = AnswerForm()
    return render_to_response('manage/add_question.html', locals(), context_instance=RequestContext(request))

def activate_question(request, quest_id=''):
    quest_id = request.GET.get('quest_id')
    obj = Question.objects.get(id=quest_id)
    obj.is_active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=manage-faq&faq_id='+str(obj.category.id))

def delete_question(request, quest_id=''):
    quest_id = request.GET.get('quest_id')
    obj = Question.objects.get(id=quest_id)
    obj.is_active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=manage-faq&faq_id='+str(obj.category.id))


#----------------------------------Article ----------------------------------------------#

def add_article(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            check=Article.objects.filter(slug=slugify(request.POST.get('name')))
            if not check:
                obj=form.save(commit=False)
                obj.slug=slugify(request.POST.get('name'))
                obj.status = 'PU'
                obj.save()
                added=True
            else:
                error = "Article Name already exists"
            return render_to_response('manage/add_article.html', locals(), context_instance=RequestContext(request))
        else:
            form = ArticleForm(request.POST, request.FILES)
        return render_to_response('manage/add_article.html', {'form':form}, context_instance=RequestContext(request))
    else:
        form = ArticleForm()
    return render_to_response('manage/add_article.html', {'form':form}, context_instance=RequestContext(request))



def edit_article(request, art_id=''):
    edit=True
    if art_id== '':
        art_id=request.GET.get('art_id', '')
    article=Article.objects.get(id=art_id)
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES,instance =article)
        if form.is_valid():
            if not has_changed(instance=article,field='name'):
                form.save()
                edit_done=True
                return render_to_response('manage/add_article.html', locals(), context_instance=RequestContext(request))
            else:
                check=Article.objects.filter(name__iexact=request.POST.get('name'))
                if not check:
                    form.save()
                    edit_done=True
                    return render_to_response('manage/add_article.html', locals(), context_instance=RequestContext(request))
                else:
                    error= "Article name already exist"
                    form = ArticleForm(request.POST, request.FILES,instance = article)
                return render_to_response('manage/add_article.html', locals(), context_instance=RequestContext(request))
        else:
            form = ArticleForm(request.POST, request.FILES,instance =article )
        return render_to_response('manage/add_article.html', locals(), context_instance=RequestContext(request))
    else:
        form = ArticleForm(instance=article)
    return render_to_response('manage/add_article.html', locals(), context_instance=RequestContext(request))



def delete_article(request, id='',next=''):
    if id == '':
        id = request.GET.get('id')
    if next == "":
        next = request.GET.get('next')
    obj = Article.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect(next)

def activate_article(request, id='',next=''):
    if id == '':
        id = request.GET.get('id')
    if next == "":
        next = request.GET.get('next')
    obj = Article.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect(next)

#----------------------------------Image ----------------------------------------------#

def add_image(request):
    key = request.GET.get('key')
    gal_id = request.GET.get('ct_id')
    if request.method== "POST":
        form=ImageForm(request.POST,request.FILES)
        if form.is_valid():
            obj= form.save(commit=False)
            obj.content_type = ContentType.objects.get(name__iexact = key)
            obj.object_id = gal_id
            obj.listingOrder = 0
            obj.status = 'PU'
            obj.save()
            return render_to_response('manage/add_image.html', {'added':True,'gal_id':gal_id,'key':key}, context_instance=RequestContext(request))
        else:
            form=ImageForm(request.POST,request.FILES)
        return render_to_response('manage/add_image.html', {'form':form,'gal_id':gal_id,'key':key}, context_instance=RequestContext(request))
    else:
        form=ImageForm()
    return render_to_response('manage/add_image.html', {'form':form,'gal_id':gal_id,'key':key}, context_instance=RequestContext(request))


def edit_image(request, img_id=''):
    if img_id == '':
        img_id=request.GET.get('img_id')
    image=Image.objects.get(id=img_id)
    if request.method== "POST":
        form=ImageForm(request.POST,request.FILES,instance=image)
        if form.is_valid():
            form.save()
            return render_to_response('manage/add_image.html', {'edit_done':True, 'img_id':img_id}, context_instance=RequestContext(request))
        else:
            form=ImageForm(request.POST,request.FILES)
        return render_to_response('manage/add_image.html', {'form':form, 'edit':True, 'img_id':img_id}, context_instance=RequestContext(request))
    else:
        form=ImageForm(instance=image)
    return render_to_response('manage/add_image.html', {'form':form, 'edit':True, 'img_id':img_id}, context_instance=RequestContext(request))




def delete_image(request, img_id='',key=''):
    if key == '':
        key = request.GET.get('key')
    next = request.GET.get('next')
    art_id = request.GET.get('art_id','')
    if img_id == '':
        img_id = request.GET.get('img_id')
    ngo_id = request.GET.get('ngo_id')
    gal_id = request.GET.get('gal_id')
    obj = Image.objects.get(id=img_id)
    obj.active = False
    obj.save()
    if key =='home-banner':
        return HttpResponseRedirect('/manage/?key='+str(key))
    elif key =='manage-articles':
        return HttpResponseRedirect('/manage/?key=manage-articles&art_id='+art_id)
    elif key =='manage-ngos':
        return HttpResponseRedirect('/manage/?key=manage-ngos&ngo_id='+ngo_id)
    elif key == 'gallery':
        return HttpResponseRedirect('/manage/?key=gallery')
    elif key == 'event':
        return HttpResponseRedirect('/manage/?key=event')
    elif key =='manage-gallery':
        return HttpResponseRedirect('/manage/?key=manage-gallery&gal_id='+gal_id)
    else:
        return HttpResponseRedirect('/manage-home/')



def activate_image(request, img_id='',key=''):
    if key == '':
        key = request.GET.get('key')
    next = request.GET.get('next')
    art_id = request.GET.get('art_id','')
    if img_id == '':
        img_id = request.GET.get('img_id')
    ngo_id = request.GET.get('ngo_id')
    gal_id = request.GET.get('gal_id')
    obj = Image.objects.get(id=img_id)
    obj.active = True
    obj.save()
    if key =='home-banner':
        return HttpResponseRedirect('/manage/?key='+str(key))
    elif key =='manage-articles':
        return HttpResponseRedirect('/manage/?key=manage-articles&art_id='+art_id)
    elif key =='manage-ngos':
        return HttpResponseRedirect('/manage/?key=manage-ngos&ngo_id='+ngo_id)
    elif key == 'gallery':
        return HttpResponseRedirect('/manage/?key=gallery')
    elif key =='manage-gallery':
        return HttpResponseRedirect('/manage/?key=manage-gallery&gal_id='+gal_id)
    elif key == 'event':
        return HttpResponseRedirect('/manage/?key=event')
    else:
        return HttpResponseRedirect('/manage-home/')


#----------------------------------Link ----------------------------------------------#

def add_link(request):
    key = request.GET.get('key')
    gal_id = request.GET.get('ct_id')
    if request.method== "POST":
        form=LinkForm(request.POST,request.FILES)
        if form.is_valid():
            obj= form.save(commit=False)
            obj.content_type = ContentType.objects.get(name__iexact = key)
            obj.object_id = gal_id
            obj.listingOrder = 0
            obj.status = 'PU'            
            obj.save()
            return render_to_response('manage/add_link.html', {'added':True,'gal_id':gal_id,'key':key}, context_instance=RequestContext(request))
        else:
            form=LinkForm(request.POST,request.FILES)
        return render_to_response('manage/add_link.html', {'form':form,'gal_id':gal_id,'key':key}, context_instance=RequestContext(request))
    else:
        form=LinkForm()
    return render_to_response('manage/add_link.html', {'form':form,'gal_id':gal_id,'key':key}, context_instance=RequestContext(request))



def edit_link(request, link_id=''):
    if link_id == '':
        link_id = request.GET.get('link_id')
    link=Link.objects.get(id = link_id)
    if request.method== "POST":
        form=LinkForm(request.POST,request.FILES,instance=link)
        if form.is_valid():
            form.save()
            return render_to_response('manage/add_link.html', {'edit_done':True, 'link_id':link_id}, context_instance=RequestContext(request))
        else:
            form=LinkForm(request.POST,request.FILES)
        return render_to_response('manage/add_link.html', {'form':form, 'edit':True, 'link_id':link_id}, context_instance=RequestContext(request))
    else:
        form=LinkForm(instance=link)
    return render_to_response('manage/add_link.html', {'form':form, 'edit':True, 'link_id':link_id}, context_instance=RequestContext(request))


def delete_link(request, link_id=''):
    if link_id == '':
        link_id = request.GET.get('link_id')
    art_id = request.GET.get('art_id','')
    ngo_id = request.GET.get('ngo_id', '')
    project_id = request.GET.get('project_id', '')
    key = request.GET.get('key')
    obj = Link.objects.get(id=link_id)
    obj.active = False
    obj.save()
    if key == 'event':
        return HttpResponseRedirect('/manage/?key=event')
    elif key == 'manage-articles':
        return HttpResponseRedirect('/manage/?key=manage-articles&art_id='+art_id)
    elif key == 'manage-sections':
        return HttpResponseRedirect('/manage/?key=manage-sections&art_id='+art_id)
    elif key == 'manage-ngos':
        return HttpResponseRedirect('/manage/?key=manage-ngos&ngo_id='+ngo_id)
    elif key == 'manage-project':
        return HttpResponseRedirect('/manage/?key=manage-project&project_id='+project_id)
    else:
        return HttpResponseRedirect('/manage-home/')

def activate_link(request, link_id=''):
    if link_id == '':
        link_id = request.GET.get('link_id')
    art_id = request.GET.get('art_id','')
    ngo_id = request.GET.get('ngo_id', '')
    project_id = request.GET.get('project_id', '')
    key = request.GET.get('key')
    obj = Link.objects.get(id=link_id)
    obj.active = True
    obj.save()
    if key == 'event':
        return HttpResponseRedirect('/manage/?key=event')
    elif key == 'manage-articles':
        return HttpResponseRedirect('/manage/?key=manage-articles&art_id='+art_id)
    elif key == 'manage-sections':
        return HttpResponseRedirect('/manage/?key=manage-sections&art_id='+art_id)
    elif key == 'manage-ngos':
        return HttpResponseRedirect('/manage/?key=manage-ngos&ngo_id='+ngo_id)
    elif key == 'manage-project':
        return HttpResponseRedirect('/manage/?key=manage-project&project_id='+project_id)
    else:
        return HttpResponseRedirect('/manage-home/')

#----------------------------------Attachment ----------------------------------------------#

def add_attach(request):
    key = request.GET.get('key')
    gal_id = request.GET.get('ct_id')
    if request.method== "POST":
        form=AttachmentForm(request.POST,request.FILES)
        if form.is_valid():
            obj= form.save(commit=False)
            obj.content_type = ContentType.objects.get(name__iexact = key)
            obj.object_id = gal_id
            obj.listingOrder = 0
            obj.status = 'PU'
            obj.save()
            return render_to_response('manage/add_attachment.html', {'added':True,'gal_id':gal_id,'key':key}, context_instance=RequestContext(request))
        else:
            form=AttachmentForm(request.POST,request.FILES)
        return render_to_response('manage/add_attachment.html', {'form':form,'gal_id':gal_id,'key':key}, context_instance=RequestContext(request))
    else:
        form=AttachmentForm()
    return render_to_response('manage/add_attachment.html', {'form':form,'gal_id':gal_id,'key':key}, context_instance=RequestContext(request))


def edit_attach(request, attach_id=''):
    if attach_id == '':
        attach_id = request.GET.get('attach_id')
    attach=Attachment.objects.get(id=attach_id)
    if request.method== "POST":
        form=AttachmentForm(request.POST,request.FILES,instance=attach)
        if form.is_valid():
            form.save()
            return render_to_response('manage/add_attachment.html', {'edit_done':True,'attach_id':attach_id}, context_instance=RequestContext(request))
        else:
            form=AttachmentForm(request.POST,request.FILES)
        return render_to_response('manage/add_attachment.html', {'form':form, 'edit':True,'attach_id':attach_id}, context_instance=RequestContext(request))
    else:
        form=AttachmentForm(instance=attach)
    return render_to_response('manage/add_attachment.html', {'form':form, 'edit':True,'attach_id':attach_id}, context_instance=RequestContext(request))



def delete_attach(request, attach_id=''):
    if attach_id == '':
        attach_id = request.GET.get('attach_id')
    key = request.GET.get('key')
    art_id = request.GET.get('art_id','')
    obj = Attachment.objects.get(id=attach_id)
    obj.active = False
    obj.save()
    if key == 'event':
        return HttpResponseRedirect('/manage/?key=event')
    elif key == 'manage-articles':
        return HttpResponseRedirect('/manage/?key=manage-articles&art_id='+art_id)
    elif key == 'ngo':
        return HttpResponseRedirect('/manage/?key=ngo')
    elif key == 'gallery':
        return HttpResponseRedirect('/manage/?key=gallery')
    else:
        return HttpResponseRedirect('/manage-home/')

def activate_attach(request, attach_id=''):
    if attach_id == '':
        attach_id = request.GET.get('attach_id')
    art_id = request.GET.get('art_id','')
    key = request.GET.get('key')
    obj = Attachment.objects.get(id=attach_id)
    obj.active = True
    obj.save()
    if key == 'event':
        return HttpResponseRedirect('/manage/?key=event')
    elif key == 'manage-articles':
        return HttpResponseRedirect('/manage/?key=manage-articles&art_id='+art_id)
    elif key == 'ngo':
        return HttpResponseRedirect('/manage/?key=ngo')
    else:
        return HttpResponseRedirect('/manage-home/')

#----------------------------------Code ----------------------------------------------#

def add_code(request):
    key = request.GET.get('key')
    gal_id = request.GET.get('ct_id')
    if request.method== "POST":
        form=CodeForm(request.POST,request.FILES)
        if form.is_valid():
            obj= form.save(commit=False)
            obj.content_type = ContentType.objects.get(name__iexact = key)
            obj.object_id = gal_id
            obj.listingOrder = 0
            obj.status = 'PU'
            obj.save()
            return render_to_response('manage/add_code_script.html', {'added':True,'gal_id':gal_id,'key':key}, context_instance=RequestContext(request))
        else:
            form=CodeForm(request.POST,request.FILES)
        return render_to_response('manage/add_code_script.html', {'form':form,'gal_id':gal_id,'key':key}, context_instance=RequestContext(request))
    else:
        form=CodeForm()
    return render_to_response('manage/add_code_script.html', {'form':form,'gal_id':gal_id,'key':key}, context_instance=RequestContext(request))


def edit_code(request, code_id=''):
    if code_id == '':
        code_id = request.GET.get('code_id')
    code=CodeScript.objects.get(id=code_id)
    if request.method== "POST":
        form=CodeForm(request.POST,request.FILES,instance=code)
        if form.is_valid():
            form.save()
            return render_to_response('manage/add_code_script.html', {'edit_done':True,'code_id':code_id}, context_instance=RequestContext(request))
        else:
            form=CodeForm(request.POST,request.FILES)
        return render_to_response('manage/add_code_script.html', {'form':form, 'edit':True,'code_id':code_id}, context_instance=RequestContext(request))
    else:
        form=CodeForm(instance=code)
    return render_to_response('manage/add_code_script.html', {'form':form, 'edit':True,'code_id':code_id}, context_instance=RequestContext(request))


def delete_code(request, code_id=''):
    if code_id == '':
        code_id = request.GET.get('code_id')
    key = request.GET.get('key')
    art_id = request.GET.get('art_id', '')
    obj = CodeScript.objects.get(id=code_id)
    obj.active = False
    obj.save()
    if key == 'event':
        return HttpResponseRedirect('/manage/?key=event')
    elif key == 'manage-articles':
        return HttpResponseRedirect('/manage/?key=manage-articles&art_id='+art_id)
    elif key =='ngo':
        return HttpResponseRedirect('/manage/?key=ngo')
    else:
        return HttpResponseRedirect('/manage-home/')

def activate_code(request, code_id=''):
    if code_id == '':
        code_id = request.GET.get('code_id')
    key = request.GET.get('key')
    art_id = request.GET.get('art_id', '')
    obj = CodeScript.objects.get(id=code_id)
    obj.active = True
    obj.save()
    if key == 'event':
        return HttpResponseRedirect('/manage/?key=event')
    elif key == 'manage-articles':
        return HttpResponseRedirect('/manage/?key=manage-articles&art_id='+art_id)
    elif key =='ngo':
        return HttpResponseRedirect('/manage/?key=ngo')
    else:
        return HttpResponseRedirect('/manage-home/')



#----------------------------------Corpoartes ----------------------------------------------#


def add_corporate(request):
    if request.method == "POST":
        form = CorporateForm(request.POST, request.FILES)
        if form.is_valid():
            userobj = User.objects.create_user(username=request.POST.get('email'), \
            email=request.POST.get('email'),password=request.POST.get('password'), first_name=request.POST.get('contact_person'))

            user_profile_obj = UserProfile.objects.create(user=userobj)

            state_obj = State.objects.get(id=int(request.POST.get('state')))
            csr_obj = CSR.objects.create(name=request.POST.get('name'),
            reg_no=request.POST.get('reg_no'), contact_person=user_profile_obj,
            established_on=request.POST.get('established_on'), icon=request.FILES.get('icon'),
            validity_80G=request.POST.get('validity_80G'),
            validity_80G_date=request.POST.get('validity_80G_date') if request.POST.get('validity_80G_date') and request.POST.get('validity_80G')=='VA' else None,
            validity_35AC=request.POST.get('validity_35AC'),
            validity_35AC_date=request.POST.get('validity_35AC_date') if request.POST.get('validity_35AC_date') and request.POST.get('validity_35AC')=='VA' else None,
            fcra=request.POST.get('fcra'),
            fcra_text=request.POST.get('fcra_text') if request.POST.get('fcra_text') and request.POST.get('fcra')=='VA' else None,
            fcra_date=request.POST.get('fcra_date') if request.POST.get('fcra_date') and request.POST.get('fcra')=='VA' else None,
            size=request.POST.get('size'), goal_amount = request.POST.get('goal_amount'),
            latest_fin=request.FILES.get('latest_fin'), slug=request.POST.get('slug'))

            CSR_Communication.objects.create(csr=csr_obj, web_address=request.POST.get('web_address'),
                phone1=request.POST.get('phone_no1'), mobile=request.POST.get('mobile'))
            ct_obj = ContentType.objects.get(model__iexact='csr')

            Address.objects.create(address1=request.POST.get('address1'), address2=request.POST.get('address2'), state=state_obj, city=request.POST.get('city'), content_type=ct_obj, object_id=csr_obj.id, country=Country.objects.get(id=1))

            added = True
            return render_to_response('manage/add_corporate.html', {'added':True}, context_instance=RequestContext(request))
        else:
            form = CorporateForm(request.POST, request.FILES)
        return render_to_response('manage/add_corporate.html', {'form':form}, context_instance=RequestContext(request))
    else:
        form = CorporateForm()
    return render_to_response('manage/add_corporate.html', locals(), context_instance=RequestContext(request))


def edit_corpoarte(request, corp_id=''):
    edit = True
    if corp_id == '':
        corp_id=request.GET.get('corporate_id', '')
    csr_obj = CSR.objects.get(id=corp_id)
    csr_comm = CSR_Communication.objects.get(csr=csr_obj)
    csr_address = Address.objects.get(content_type = ContentType.objects.get(model__iexact='csr'), object_id=csr_obj.id)
    if request.method == "POST":
        form = CorporateEditForm(request.POST, request.FILES)
        if form.is_valid():
            state_id = request.POST.get('state')
            csr_obj.name=request.POST.get('name')
            csr_obj.reg_no=request.POST.get('reg_no')
            csr_obj.established_on=request.POST.get('established_on')
            csr_obj.icon=request.FILES.get('icon')
            csr_obj.validity_80G=request.POST.get('validity_80G')
            csr_obj.validity_80G_date=request.POST.get('validity_80G_date') if request.POST.get('validity_80G_date') and request.POST.get('validity_80G')=='VA' else None
            csr_obj.validity_35AC=request.POST.get('validity_35AC')
            csr_obj.validity_35AC_date=request.POST.get('validity_35AC_date') if request.POST.get('validity_35AC_date') and request.POST.get('validity_35AC')=='VA' else None
            csr_obj.fcra=request.POST.get('fcra')
            csr_obj.fcra_text=request.POST.get('fcra_text') if request.POST.get('fcra_text') and request.POST.get('fcra')=='VA' else None
            csr_obj.fcra_date=request.POST.get('fcra_date') if request.POST.get('fcra_date') and request.POST.get('fcra')=='VA' else None
            csr_obj.size=request.POST.get('size')
            csr_obj.latest_fin=request.POST.get('latest_fin')
            csr_obj.save()

            user_obj = User.objects.get(username=csr_obj.contact_person.user.username)
            user_obj.first_name = request.POST['contact_person']
            user_obj.save()

            csr_comm.web_address=request.POST.get('web_address')
            csr_comm.phone1=request.POST.get('phone_no1')
            csr_comm.mobile=request.POST.get('mobile')
            csr_comm.save()

            csr_address.address1=request.POST.get('address1')
            csr_address.address2=request.POST.get('address2')
            state_obj = State.objects.get(id=state_id)
            csr_address.state=state_obj
            csr_address.city=request.POST.get('city')
            csr_address.save()

            edit_done = True
            return render_to_response('manage/add_corporate.html', locals(),\
                        context_instance=RequestContext(request))
        else:
            form = CorporateEditForm(request.POST, request.FILES)
        return render_to_response('manage/add_corporate.html',locals(), \
                    context_instance=RequestContext(request))
    else:
        form = CorporateEditForm(initial={'name':csr_obj.name,
            'reg_no':csr_obj.reg_no, 'contact_person':csr_obj.contact_person.user.first_name,
            'address1':csr_address.address1, 'city':csr_address.city, 'address2':csr_address.address2,
            'state':csr_address.state, 'phone_no1':csr_comm.phone1, 'mobile':csr_comm.mobile,
            'icon':csr_obj.icon, 'established_on':csr_obj.established_on ,
            'validity_80G':csr_obj.validity_80G, 'validity_80G_date':csr_obj.validity_80G_date,
            'validity_35AC':csr_obj.validity_35AC, 'validity_35AC_date':csr_obj.validity_35AC_date,
            'fcra':csr_obj.fcra, 'fcra_text':csr_obj.fcra_text, 'fcra_date':csr_obj.fcra_date,
            'size':csr_obj.size, 'slug':csr_obj.slug, 'web_address':csr_comm.web_address,
            'email':csr_obj.contact_person.user.email, 'latest_fin':csr_obj.latest_fin, 'goal_amount':csr_obj.goal_amount })
    return render_to_response('manage/add_corporate.html', locals(), context_instance=RequestContext(request))


def delete_corporate(request, cid=''):
    if cid == '':
        cid = int(request.GET.get('id'))
    obj = CSR.objects.get(id=cid)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=corporate')


def activate_corporate(request, cid=''):
    if cid == '':
        cid = int(request.GET.get('id'))
    obj = CSR.objects.get(id=cid)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=corporate')



from django.utils.encoding import smart_str
def format_date(d):
    d=d.split('-')
    from datetime import *
    return date(int(d[0]),int(d[1]),int(d[2]))


#----------------------------------NGO ----------------------------------------------#


def ngolist(request):
    ngo = []
    ngo = NGO.objects.all()[:20]
    return render_to_response('manage/ngolist.html',{'ngo':ngo},context_instance=RequestContext(request))



def add_ngo(request):
    check = ''
    check1 = ''
    countryobj = ''
    if request.method == "POST":
        form1 = UserFormBk(request.POST)
        form2 = UserInfoForm(request.POST)   #User Profile
        form3 = NGORegisterForm(request.POST,request.FILES)
        form4 = AddressForm(request.POST)
        form5 = CustomizeNGOFormBk(request.POST)
        if form1.is_valid() and form3.is_valid() and form4.is_valid():
            mail_id = request.POST.get('email', '')
            if User.objects.filter(email=mail_id):
                error = "This E-mail is already registered with us."
                return render_to_response("manage/ngo.html", \
                locals(),context_instance=RequestContext(request))
            try:
                check = User.objects.get(username = mail_id)
            except:
                pass
            try:
                check1 = NGO.objects.filter(slug=request.POST.get('slug'))
            except:
                pass
            if not check and not check1:
                userobj = User.objects.create_user(username=request.POST.get('email'), \
                email=request.POST.get('email'),password=request.POST.get('password'), first_name=request.POST.get('first_name'), last_name=request.POST.get('last_name'))
                title = request.POST.get('title')
                title_obj = Salutations.objects.get(id=title)
                user_profile_obj = UserProfile.objects.create(user=userobj, title=title_obj, usertype='1')
                user_details_obj = UserDetails.objects.create(user=userobj, password=request.POST.get('password'), username=request.POST.get('email'))

                state = request.POST.get('state')
                country = request.POST.get('country')
                try:
                    country_obj = Country.objects.get(name=country)
                except:
                    country_obj = Country.objects.create(name=country)
                try:
                    state_obj = State.objects.get(name=state,country=country_obj)
                except:
                    state_obj = State.objects.create(name=state,country=country_obj)
                cause = Cause.objects.get(id=request.POST.get('cause'))

                we_id = request.POST.getlist('we_are_on','')

                ngo_obj = NGO.objects.create(name=request.POST.get('name'),
                reg_no=request.POST.get('reg_no'),
                contact_person=user_profile_obj,
                established_on=request.POST.get('established_on'),
                cause = cause,
                icon=request.FILES.get('icon'),
                front_image=request.FILES.get('front_image'),
                validity_80G=request.POST.get('validity_80G'),
                validity_80G_date=request.POST.get('validity_80G_date') if request.POST.get('validity_80G_date') and request.POST.get('validity_80G')=='VA' else None,
                validity_35AC=request.POST.get('validity_35AC'),
                validity_35AC_date=request.POST.get('validity_35AC_date') if request.POST.get('validity_35AC_date') and request.POST.get('validity_35AC')=='VA' else None,
                fcra=request.POST.get('fcra'),
                fcra_text=request.POST.get('fcra_text') if request.POST.get('fcra_text') and request.POST.get('fcra')=='VA' else None,
                fcra_date=request.POST.get('fcra_date') if request.POST.get('fcra_date') and request.POST.get('fcra')=='VA' else None,
                a12=request.POST.get('a12'),
                size=request.POST.get('size'),
                credibility_norms=request.POST.get('credibility_norms') if request.POST.get('credibility_norms') else False,
                primary_focus=request.POST.get('primary_focus'),
                secondary_focus=request.POST.get('secondary_focus'),
                audited_balance_sheet=request.FILES.get('audited_balance_sheet'),
                profit_loss_statement=request.FILES.get('profit_loss_statement'),
                undertakng=request.FILES.get('undertakng'), slug=request.POST.get('slug'))

                ngo_obj.our_mission = request.POST.get('our_mission')
                
                ngo_obj.slug=request.POST.get('slug')
                ngo_obj.work_acheivement = request.POST.get('work_acheivement')
                ngo_obj.youtube_embedd = request.POST.get('youtube_embedd')
                ngo_obj.fund_utilisation_statement = request.POST.get('fund_utilisation_statement')
                ngo_obj.black_board_message = request.POST.get('black_board_message')
                ngo_keywords = str(request.POST.get('ngo_keywords', ''))
                keywords_list = ngo_keywords.split(',')
                for i in keywords_list:
                    if i == '':
                        pass
                    else:
                        NGO_Keywords.objects.get_or_create(name=i)
                        keyword_obj = NGO_Keywords.objects.filter(name=i)[0]
                        ngo_obj.ngo_keywords.add(keyword_obj)

                ngo_obj.for_donate_mail = request.POST.get('for_donate_mail', '')
                ngo_obj.for_fundraise_page = request.POST.get('for_fundraise_page', '')
                ngo_obj.for_every_month_report = request.POST.get('for_every_month_report', '')
                ngo_obj.display_in_main = request.POST.get('display_in_event', '')
                ngo_obj.accept_donation = request.POST.get('accept_donation', '')
                we_are_text = []
                for i in request.POST.getlist('we_are_on', ''):
                    we_are_text.append(request.POST.get('we_are_text_'+i, ''))
                for i in we_id:
                    socilnw = Social_Network.objects.get(id=i)
                    ngo_obj.we_are_on.add(socilnw)
                we_list = [i.name for i in ngo_obj.we_are_on.all()]
                t = dict(zip(we_list, we_are_text))
                for name,url in t.iteritems():
                    Link.objects.create(name=name, URL=url, content_type=ContentType.objects.get(model__iexact='ngo'), object_id=ngo_obj.id)

                ngo_obj.save()

                NGO_Communication.objects.create(ngo=ngo_obj, web_address=request.POST.get('web_address'),
                phone1=request.POST.get('phone1'), mobile=request.POST.get('mobile'))
                request.session['ngo_id'] = ngo_obj.id
                ct_obj = ContentType.objects.get(model__iexact='ngo')

                Address.objects.create(address1=request.POST.get('address1'), address2=request.POST.get('address2'), state=state_obj, city=request.POST.get('city'),
                content_type=ct_obj, object_id=ngo_obj.id, country=country_obj, pincode=request.POST.get('pincode'))
                if request.POST.get('appeal1_amount'):
                    NGO_appeals.objects.create(ngo=ngo_obj, amount=request.POST.get('appeal1_amount'), appeal_for=request.POST.get('appeal1_for'))
                if request.POST.get('appeal2_amount'):
                    NGO_appeals.objects.create(ngo=ngo_obj, amount=request.POST.get('appeal2_amount'), appeal_for=request.POST.get('appeal2_for'))
                if request.POST.get('appeal3_amount'):
                    NGO_appeals.objects.create(ngo=ngo_obj, amount=request.POST.get('appeal3_amount'), appeal_for=request.POST.get('appeal3_for'))
                added = True
            else:
                error = "Slug already exists."
                return render_to_response("manage/ngo.html", locals(), context_instance=RequestContext(request))
    else:
        form1 = UserFormBk()
        form2 = UserInfoForm()
        form3 = NGORegisterForm()
        form4 = AddressForm()
        form5 = CustomizeNGOFormBk()
    return render_to_response("manage/ngo.html", locals(), context_instance=RequestContext(request))



def edit_ngo(request, ngo_id=''):

    check = ''
    edit = True
    if ngo_id == '':
        ngo_id=int(request.GET.get('ngo_id', ''))
    ngo_obj = NGO.objects.get(id=ngo_id)
    ct_obj = ContentType.objects.get(name__iexact='ngo')
    ngo_add = Address.objects.filter(content_type=ct_obj, object_id=ngo_id)[0]
    ngo_comm_obj = NGO_Communication.objects.get(ngo=ngo_obj)
    ngo_appeals = NGO_appeals.objects.filter(ngo=ngo_obj)
    userprofile_obj = ngo_obj.contact_person
    user = userprofile_obj.user
    if request.method == "POST":
        form1 = UserForm(request.POST, instance=user)
        form2 = UserInfoForm(request.POST, instance=userprofile_obj)   #User Profile
        form3 = NGORegisterForm(request.POST,request.FILES)
        form4 = AddressForm(request.POST, instance=ngo_add)
        form5 = CustomizeNGOFormBk(request.POST)
        if form1.is_valid() and form3.is_valid() and form4.is_valid():
            mail_id = request.POST.get('email', '')
            if not User.objects.filter(email=mail_id).exclude(email=mail_id):
                if not NGO.objects.filter(slug=request.POST.get('slug')).exclude(id=ngo_obj.id).exists():
                    userobj = form1.save( commit=False)
                    userobj.username = request.POST.get('email', '')
                    userobj.save()
                    user_profile_obj = UserProfile.objects.get(user=userobj)
                    title = request.POST.get('title')
                    title_obj = Salutations.objects.get(id=title)
                    user_profile_obj.title=title_obj
                    user_profile_obj.usertype = '1'
                    user_profile_obj.save()
                    ngo_obj.name=request.POST.get('name')
                    ngo_obj.reg_no=request.POST.get('reg_no')
                    ngo_obj.established_on=request.POST.get('established_on')
                    if request.FILES.get('icon'):
                        ngo_obj.icon=request.FILES.get('icon')
                    if request.FILES.get('front_image'):
                        ngo_obj.front_image=request.FILES.get('front_image')
                    ngo_obj.validity_80G=request.POST.get('validity_80G')
                    ngo_obj.validity_80G_date=request.POST.get('validity_80G_date') if request.POST.get('validity_80G_date') and request.POST.get('validity_80G')=='VA' else None
                    ngo_obj.validity_35AC=request.POST.get('validity_35AC')
                    ngo_obj.validity_35AC_date=request.POST.get('validity_35AC_date') if request.POST.get('validity_35AC_date') and request.POST.get('validity_35AC')=='VA' else None
                    ngo_obj.fcra=request.POST.get('fcra')
                    ngo_obj.fcra_text=request.POST.get('fcra_text') if request.POST.get('fcra_text') and request.POST.get('fcra')=='VA' else None
                    ngo_obj.fcra_date=request.POST.get('fcra_date') if request.POST.get('fcra_date') and request.POST.get('fcra')=='VA' else None
                    ngo_obj.a12=request.POST.get('a12')

                    ngo_obj.size=request.POST.get('size')
                    ngo_obj.cause = Cause.objects.get(id=request.POST.get('cause'))
                    ngo_obj.credibility_norms=request.POST.get('credibility_norms') if request.POST.get('credibility_norms') else False
                    ngo_obj.primary_focus=request.POST.get('primary_focus')
                    ngo_obj.secondary_focus=request.POST.get('secondary_focus')
                    ngo_obj.our_mission = request.POST.get('our_mission')
                    ngo_obj.work_acheivement = request.POST.get('work_acheivement')
                    ngo_obj.for_donate_mail = request.POST.get('for_donate_mail', '')
                    ngo_obj.for_fundraise_page = request.POST.get('for_fundraise_page', '')
                    ngo_obj.for_every_month_report = request.POST.get('for_every_month_report', '')
                    ngo_obj.youtube_embedd = request.POST.get('youtube_embedd')
                    ngo_obj.fund_utilisation_statement = request.POST.get('fund_utilisation_statement')
                    ngo_obj.display_in_main = request.POST.get('display_in_event', '')
                    ngo_obj.black_board_message = request.POST.get('black_board_message')
                    ngo_obj.slug = request.POST.get('slug')
                    ngo_obj.accept_donation = request.POST.get('accept_donation', '')
                    if request.FILES.get('audited_balance_sheet'):
                        ngo_obj.audited_balance_sheet=request.FILES.get('audited_balance_sheet')
                    if request.FILES.get('profit_loss_statement'):
                        ngo_obj.profit_loss_statement=request.FILES.get('profit_loss_statement')
                    if request.FILES.get('undertakng'):
                        ngo_obj.undertakng=request.FILES.get('undertakng')
                    ngo_obj.save()

                    ngo_comm_obj.city=request.POST.get('city')
                    ngo_comm_obj.web_address=request.POST.get('web_address')
                    ngo_comm_obj.phone1=request.POST.get('phone1')
                    ngo_comm_obj.mobile=request.POST.get('mobile')
                    ngo_comm_obj.save()
                    state = request.POST.get('state')
                    country = request.POST.get('country')
                    try:
                        country_obj = Country.objects.get(name=country)
                    except:
                        country_obj = Country.objects.create(name=country)
                    try:
                        state_obj = State.objects.get(name=state,country=country_obj)
                    except:
                        state_obj = State.objects.create(name=state,country=country_obj)
                    f=form4.save(commit=False)
                    f.state = state_obj
                    f.country = country_obj
                    f.save()
                    try:
                        if ngo_appeals[0]:
                            ngo_appeal_obj = ngo_appeals[0]
                            ngo_appeal_obj.amount=request.POST.get('appeal1_amount')
                            ngo_appeal_obj.appeal_for=request.POST.get('appeal1_for')
                            ngo_appeal_obj.save()
                    except:
                        if not request.POST.get('appeal1_amount') == '':
                            NGO_appeals.objects.create(ngo=ngo_obj, amount=request.POST.get('appeal1_amount'), appeal_for=request.POST.get('appeal1_for'))
                    appeal2_amount = request.POST.get('appeal2_amount')
                    appeal2_for = request.POST.get('appeal2_for')
                    try:
                        if ngo_appeals[1]:
                            ngo_appeal_obj = ngo_appeals[1]
                            ngo_appeal_obj.amount=request.POST.get('appeal2_amount')
                            ngo_appeal_obj.appeal_for=request.POST.get('appeal2_for')
                            ngo_appeal_obj.save()
                    except:
                        if not appeal2_amount == '':
                            NGO_appeals.objects.create(ngo=ngo_obj, amount=appeal2_amount if appeal2_amount else 0, appeal_for=appeal2_for if appeal2_for else '')
                    appeal3_amount = request.POST.get('appeal3_amount')
                    appeal3_for = request.POST.get('appeal3_for')
                    try:
                        if ngo_appeals[2]:
                            ngo_appeal_obj = ngo_appeals[2]
                            ngo_appeal_obj.amount=request.POST.get('appeal3_amount')
                            ngo_appeal_obj.appeal_for=request.POST.get('appeal3_for')
                            ngo_appeal_obj.save()
                    except:
                        if not appeal3_amount == '':
                            NGO_appeals.objects.create(ngo=ngo_obj, amount=appeal3_amount if appeal3_amount else 0, appeal_for=appeal3_for if appeal3_for else '')
                    edit_done = True
                else:
                    error = "Slug already exists."
                    return render_to_response("manage/ngo.html", locals(), context_instance=RequestContext(request))
            else:
                error = "This E-mail is already registered with us."
                return render_to_response("manage/ngo.html", locals(), context_instance=RequestContext(request))
    else:
        form1 = UserForm(instance=user)
        form2 = UserInfoForm(instance=userprofile_obj)   #User Profile
        form3 = NGORegisterForm(initial={'name':ngo_obj.name,
            'reg_no':ngo_obj.reg_no, 'contact_person':ngo_obj.contact_person.user.first_name,
            'address1':ngo_add.address1, 'city':ngo_add.city, 'address2':ngo_add.address2,
            'state':ngo_add.state, 'phone_no1':ngo_comm_obj.phone1, 'mobile':ngo_comm_obj.mobile,
            'icon':ngo_obj.icon, 'front_image':ngo_obj.front_image, 'established_on':ngo_obj.established_on ,
            'validity_80G':ngo_obj.validity_80G, 'validity_80G_date':ngo_obj.validity_80G_date,
            'validity_35AC':ngo_obj.validity_35AC, 'validity_35AC_date':ngo_obj.validity_35AC_date,
            'fcra':ngo_obj.fcra, 'fcra_text':ngo_obj.fcra_text, 'fcra_date':ngo_obj.fcra_date,
            'a12':ngo_obj.a12, 'size':ngo_obj.size, 'cause':ngo_obj.cause, 'credibility_norms':ngo_obj.credibility_norms,
            'primary_focus':ngo_obj.primary_focus, 'secondary_focus':ngo_obj.secondary_focus,
            'ngo_keywords': ngo_obj.ngo_keywords.all(), 'slug':ngo_obj.slug, 'web_address':ngo_comm_obj.web_address,
            'email':ngo_obj.contact_person.user.email, 'audited_balance_sheet':ngo_obj.audited_balance_sheet,
            'profit_loss_statement':ngo_obj.profit_loss_statement, 'undertakng':ngo_obj.undertakng,
            'youtube_embedd':ngo_obj.youtube_embedd,'black_board_message':ngo_obj.black_board_message,
            'accept_donation':ngo_obj.accept_donation})
        form4 = AddressForm(instance=ngo_add)
        if ngo_appeals:
            if ngo_appeals[0]:
                form5 = CustomizeNGOFormBk(initial ={'our_mission':ngo_obj.our_mission,
                    'work_acheivement':ngo_obj.work_acheivement,
                    'for_donate_mail':ngo_obj.for_donate_mail,
                    'for_fundraise_page':ngo_obj.for_fundraise_page,
                    'for_every_month_report':ngo_obj.for_every_month_report,
                    'we_are_on':ngo_obj.we_are_on.all(),
                    'appeal1_amount':ngo_appeals[0].amount, 'appeal1_for':ngo_appeals[0].appeal_for })
            try:
                if ngo_appeals[0] and ngo_appeals[1]:
                    form5 = CustomizeNGOFormBk(initial ={'our_mission':ngo_obj.our_mission,
                        'work_acheivement':ngo_obj.work_acheivement,
                        'for_donate_mail':ngo_obj.for_donate_mail,
                        'for_fundraise_page':ngo_obj.for_fundraise_page,
                        'for_every_month_report':ngo_obj.for_every_month_report,
                        'we_are_on':ngo_obj.we_are_on.all(),
                        'appeal1_amount':ngo_appeals[0].amount, 'appeal1_for':ngo_appeals[0].appeal_for, 
                        'appeal2_amount':ngo_appeals[1].amount, 'appeal2_for':ngo_appeals[1].appeal_for })
            except:
                pass
            try:
                if ngo_appeals[0] and ngo_appeals[1] and ngo_appeals[2]:
                    form5 = CustomizeNGOFormBk(initial ={'our_mission':ngo_obj.our_mission,
                        'work_acheivement':ngo_obj.work_acheivement,
                        'for_donate_mail':ngo_obj.for_donate_mail,
                        'for_fundraise_page':ngo_obj.for_fundraise_page,
                        'for_every_month_report':ngo_obj.for_every_month_report,
                        'we_are_on':ngo_obj.we_are_on.all(),
                        'appeal1_amount':ngo_appeals[0].amount, 'appeal1_for':ngo_appeals[0].appeal_for, 
                        'appeal2_amount':ngo_appeals[1].amount, 'appeal2_for':ngo_appeals[1].appeal_for, 
                        'appeal3_amount':ngo_appeals[2].amount, 'appeal3_for':ngo_appeals[2].appeal_for })
            except:
                pass
        else:
            form5 = CustomizeNGOFormBk(initial ={'our_mission':ngo_obj.our_mission,
                    'work_acheivement':ngo_obj.work_acheivement,
                    'for_donate_mail':ngo_obj.for_donate_mail,
                    'for_fundraise_page':ngo_obj.for_fundraise_page,
                    'for_every_month_report':ngo_obj.for_every_month_report})
    return render_to_response("manage/ngo.html", locals(), context_instance=RequestContext(request))

def delete_ngo(request):
    ngo_id = request.GET.get('id')
    obj = NGO.objects.get(id=ngo_id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=ngo')


def activate_ngo(request):
    ngo_id = request.GET.get('id')
    obj = NGO.objects.get(id=ngo_id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=ngo')

#----------------------------------NGO Communication ----------------------------------------------#
def add_ngo_comm(request):
    link_obj = ''
    key = request.GET.get('key')
    gal_id = request.GET.get('ct_id')
    sn = Social_Network.objects.filter(active=True)
    if request.method== "POST":
        for i in sn:
            try:
                if not request.POST.get(i.name) == '':
                    link_obj = Link.objects.get(name=i.name, 
                            content_type = ContentType.objects.get(name__iexact = 'ngo'),
                            object_id = gal_id)
            except:
                pass
            if not link_obj:
                if not request.POST.get(i.name) == '':
                    obj= Link.objects.create(name=i.name, URL=request.POST.get(i.name), 
                                content_type = ContentType.objects.get(name__iexact = 'ngo'),
                                object_id = gal_id)
                    added = True
            else:
                msg = link_obj.name + " Communication link already added please add contents which are not added before"
    return render_to_response('manage/add_ngo_comm.html', locals(), context_instance=RequestContext(request))


def edit_ngo_comm(request, link_id=''):
    edit = True
    link_id = request.GET.get('link_id')
    ngo_id = request.GET.get('ngo_id')
    link_obj = Link.objects.get(id=link_id)
    if request.method== "POST":
        link_obj.URL=request.POST.get(link_obj.name)
        link_obj.save()
        edit_done=True
    return render_to_response('manage/add_ngo_comm.html', locals(), context_instance=RequestContext(request))


#---------------------------------- Donation  ----------------------------------------------#

def add_donation(request):
    if request.method== "POST":
        form=DonationForm(request.POST)
        if form.is_valid():
            obj = form.save(commit = False)
            obj.object_id = request.user
            obj.state = request.POST.get('state')
            obj.country = request.POST.get('country')
            obj.save()
            added = True
            return render_to_response('manage/donation.html', locals(), context_instance=RequestContext(request))
        else:
            form=DonationForm(request.POST)
        return render_to_response('manage/donation.html', locals(), context_instance=RequestContext(request))
    else:
        form=DonationForm()
    return render_to_response('manage/donation.html', locals(), context_instance=RequestContext(request))


def edit_donation(request,don_id=''):
    edit = True
    if don_id == '':
        don_id = int(request.GET.get('don_id'))
    don_obj = Donation.objects.get(id=don_id)
    #form = DonationForm(instance=don_obj)
    if request.method == "POST":
        form = DonationForm(request.POST,instance=don_obj)
        if form.is_valid():
            f = form.save(commit=False)
            f.state = request.POST.get('state')
            f.country = request.POST.get('country')
            f.save()
            edit_done = True
        else:
            form = DonationForm(request.POST,instance=don_obj)
    else:
        form = DonationForm(instance=don_obj)
    return render_to_response('manage/donation.html',locals(),context_instance=RequestContext(request))


# -------------------------------- Our Project--------------------------------------- ---------------- #

def add_project(request):
    ngo_id=''
    we_are_text = []
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save(commit=False)
            f.content_type = ContentType.objects.get(model__iexact="ngo")
            f.object_id = request.GET.get('ngo_id')
            f.save()
            we_are_on = request.POST.getlist('we_are_on')
            for i in we_are_on:
                socilnw = Social_Network.objects.get(id=i)
                f.we_are_on.add(socilnw)
            we_list = [i.name for i in f.we_are_on.all()]
            for i in request.POST.getlist('we_are_on', ''):
                we_are_text.append(request.POST.get('we_are_text_'+i, ''))
            t = dict(zip(we_list, we_are_text))
            for name,url in t.iteritems():
                Link.objects.create(name=name, URL=url, content_type=ContentType.objects.get(model__iexact='project'), object_id=f.id)
            added = True
            return render_to_response('manage/add_project.html', locals(), context_instance=RequestContext(request))
        else:
            form = ProjectForm(request.POST, request.FILES)
        return render_to_response('manage/add_project.html', locals(), context_instance=RequestContext(request))
    else:
        ngo_id = request.GET.get('ngo_id')
        form = ProjectForm()
    return render_to_response('manage/add_project.html', locals(), context_instance=RequestContext(request))



def edit_project(request):
    edit = True
    we_are_text = []
    project_id=request.GET.get('project_id')
    project_obj=Project.objects.get(id=project_id)
    if request.method== "POST":
        form=ProjectForm(request.POST,instance = project_obj)
        if form.is_valid():
            form.save()
            edit_done = True
        else:
            form=ProjectForm(request.POST)
            return render_to_response('manage/add_project.html', locals(), context_instance=RequestContext(request))
    else:
        form=ProjectForm(instance = project_obj)
        return render_to_response('manage/add_project.html', locals(), context_instance=RequestContext(request))
    return render_to_response('manage/add_project.html', locals(), context_instance=RequestContext(request))


def delete_project(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Project.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=projects')

def activate_project(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Project.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=projects')


# -------------------------------- Staff Type --------------------------------------- ---------------- #


def add_staff_type(request):
   
    if request.method == "POST":
        form = Staff_typeForm(request.POST)
        if form.is_valid():
            check=Staff_Type.objects.filter(name__iexact=request.POST.get('name'))
            if not check:
                f= form.save(commit=False)
                f.slug = slugify(request.POST.get('name'))
                f.save()
                return render_to_response('manage/add_staff_type.html', {'added':True}, context_instance=RequestContext(request))
            else:
                error= "Staff type name already exist."
                form = Staff_typeForm(request.POST)
                return render_to_response('manage/add_staff_type.html', {'form':form}, context_instance=RequestContext(request))
        else:
            form = Staff_typeForm(request.POST)
        return render_to_response('manage/add_staff_type.html', {'form':form}, context_instance=RequestContext(request))
    else:
        form = Staff_typeForm()
    return render_to_response('manage/add_staff_type.html', {'form':form}, context_instance=RequestContext(request))


def edit_staff_type(request, staff_id=''):
    if staff_id== '':
        staff_id=request.GET.get('staff_id', '')
    stafftype = Staff_Type.objects.get(id=staff_id)
    if request.method == "POST":
        form = Staff_typeForm(request.POST, instance = stafftype)
        if form.is_valid():
            if not has_changed(instance= stafftype,field='name'):
                    form.save()
                    return render_to_response('manage/add_staff_type.html', {'edit_done':True, 'staff_id':staff_id}, context_instance=RequestContext(request))
            else:
                check=Staff_Type.objects.filter(name__iexact=request.POST.get('name'))
                if not check:
                    form.save()
                    return render_to_response('manage/add_staff_type.html', {'edit_done':True, 'staff_id':staff_id}, context_instance=RequestContext(request))
                else:
                    error= "Category name already exist"
                    form = Staff_typeForm(request.POST)
                    return render_to_response('manage/add_staff_type.html', {'form':form, 'edit':True, 'staff_id':staff_id}, context_instance=RequestContext(request))    
        else:
            form = Staff_typeForm(request.POST)
        return render_to_response('manage/add_staff_type.html', {'form':form, 'edit':True, 'staff_id':staff_id}, context_instance=RequestContext(request))
    else:
        form = Staff_typeForm(instance= stafftype)
    return render_to_response('manage/add_staff_type.html', {'form':form, 'edit':True, 'staff_id':staff_id}, context_instance=RequestContext(request))

def delete_staff_type(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Staff_Type.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=staff-type')

def activate_staff_type(request, id=''):
    
    if id == '':
        id = request.GET.get('id')
    obj = Staff_Type.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=staff-type')

# -------------------------------- Manage News --------------------------------------- ---------------- #


def add_news(request):
   
    if request.method == "POST":
        form = NewsForm(request.POST)
        if form.is_valid():
            form.save()
            return render_to_response('manage/add_news.html', {'added':True}, context_instance=RequestContext(request))
        else:
            form = NewsForm(request.POST)
        return render_to_response('manage/add_news.html', {'form':form}, context_instance=RequestContext(request))
    else:
        form = NewsForm()
    return render_to_response('manage/add_news.html', {'form':form}, context_instance=RequestContext(request))


def edit_news(request, news_id=''):
    if news_id== '':
        news_id=request.GET.get('news_id', '')
    news = News.objects.get(id=news_id)
    if request.method == "POST":
        form = NewsForm(request.POST, instance = news)
        if form.is_valid():
            form.save()
            return render_to_response('manage/add_news.html', {'edit_done':True, 'news_id':news_id}, context_instance=RequestContext(request))
        else:
            form = NewsForm(request.POST)
        return render_to_response('manage/add_news.html', {'form':form, 'edit':True, 'news_id':news_id}, context_instance=RequestContext(request))
    else:
        form = NewsForm(instance= news)
    return render_to_response('manage/add_news.html', {'form':form, 'edit':True, 'news_id':news_id}, context_instance=RequestContext(request))

def delete_news(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = News.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=news')

def activate_news(request, id=''):
    
    if id == '':
        id = request.GET.get('id')
    obj = News.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=news')

# -------------------------------- Manage Hotels --------------------------------------- ---------------- #


def add_hotels(request):
    event_id = request.GET.get('event')
    if request.method == "POST":
        form = Contibuting_HotelsForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save(commit=False)
            f.slug = slugify(request.POST.get('name'))
            f.save()
            try:
                event_obj = Event.objects.get(id=event_id)
                event_obj.contributing_hotels.add(f)
            except:
                pass
            added = True
            return render_to_response('manage/add_hotels.html', locals(), context_instance=RequestContext(request))
        else:
            form = Contibuting_HotelsForm(request.POST, request.FILES)
        return render_to_response('manage/add_hotels.html', locals(), context_instance=RequestContext(request))
    else:
        form = Contibuting_HotelsForm()
    return render_to_response('manage/add_hotels.html', locals(), context_instance=RequestContext(request))


def edit_hotels(request, hotels_id=''):
    if hotels_id== '':
        hotels_id=request.GET.get('hotels_id', '')
    hotels = Contributing_Hotels.objects.get(id=hotels_id)
    if request.method == "POST":
        form = Contibuting_HotelsForm(request.POST, request.FILES, instance = hotels)
        if form.is_valid():
            form.save()
            return render_to_response('manage/add_hotels.html', {'edit_done':True, 'hotels_id':hotels_id}, context_instance=RequestContext(request))
        else:
            form = Contibuting_HotelsForm(request.POST, request.FILES)
        return render_to_response('manage/add_hotels.html', {'form':form, 'edit':True, 'hotels_id':hotels_id}, context_instance=RequestContext(request))
    else:
        form = Contibuting_HotelsForm(instance= hotels)
    return render_to_response('manage/add_hotels.html', {'form':form, 'edit':True, 'hotels_id':hotels_id}, context_instance=RequestContext(request))

def delete_hotels(request, id=''):
    if id == '':
        id = request.GET.get('id')
    eid = request.GET.get('event_id')
    obj = Contributing_Hotels.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=manage-event&event_id='+eid)

def activate_hotels(request, id=''):
    
    if id == '':
        id = request.GET.get('id')
    eid = request.GET.get('event_id')
    obj = Contributing_Hotels.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=manage-event&event_id='+eid)

# -------------------------------- Manage Contributing Tables --------------------------------------- ---------------- #


def add_contributing_tables(request):
    event_id = request.GET.get('event')
    if request.method == "POST":
        form = Corporate_TablesForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save(commit=False)
            f.slug = slugify(request.POST.get('name'))
            f.save()
            try:
                event_obj = Event.objects.get(id=event_id)
                event_obj.corporate_tables.add(f)
            except:
                pass
            added = True
            return render_to_response('manage/add_tables.html', locals(), context_instance=RequestContext(request))
        else:
            form = Corporate_TablesForm(request.POST, request.FILES)
        return render_to_response('manage/add_tables.html', locals(), context_instance=RequestContext(request))
    else:
        form = Corporate_TablesForm()
    return render_to_response('manage/add_tables.html', locals(), context_instance=RequestContext(request))


def edit_contributing_tables(request, tables_id=''):
    if tables_id== '':
        tables_id=request.GET.get('tables_id', '')
    tables = Corporate_Tables.objects.get(id=tables_id)
    if request.method == "POST":
        form = Corporate_TablesForm(request.POST, request.FILES, instance = tables)
        if form.is_valid():
            form.save()
            return render_to_response('manage/add_tables.html', {'edit_done':True, 'tables_id':tables_id}, context_instance=RequestContext(request))
        else:
            form = Corporate_TablesForm(request.POST, request.FILES)
        return render_to_response('manage/add_tables.html', {'form':form, 'edit':True, 'tables_id':tables_id}, context_instance=RequestContext(request))
    else:
        form = Corporate_TablesForm(instance= tables)
    return render_to_response('manage/add_tables.html', {'form':form, 'edit':True, 'tables_id':tables_id}, context_instance=RequestContext(request))

def delete_contributing_tables(request, id=''):
    if id == '':
        id = request.GET.get('id')
    eid = request.GET.get('event_id')
    obj = Corporate_Tables.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=manage-event&event_id='+eid)

def activate_contributing_tables(request, id=''):
    
    if id == '':
        id = request.GET.get('id')
    eid = request.GET.get('event_id')
    obj = Corporate_Tables.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=manage-event&event_id='+eid)



#---------------------------------- Our Team (Staff)  ----------------------------------------------#

def add_staff(request):
    if request.method == "POST":
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save(commit=False)
            f.slug = slugify(request.POST.get('name'))
            f.save()
            added = True
            return render_to_response('manage/staff.html', locals(), context_instance=RequestContext(request))
        else:
            form = StaffForm(request.POST, request.FILES)
        return render_to_response('manage/staff.html', locals(), context_instance=RequestContext(request))
    else:
        form = StaffForm()
    return render_to_response('manage/staff.html', locals(), context_instance=RequestContext(request))


def edit_staff(request, staff_id=''):
    edit = True
    if staff_id == '':
        staff_id = request.GET.get('staff_id')
    staff = Staff.objects.get(id=staff_id)
    if request.method == "POST":
        form = StaffForm(request.POST,request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            edit_done = True
            return render_to_response('manage/staff.html', locals(), context_instance=RequestContext(request))
        else:
            form = StaffForm(request.POST,request.FILES)
        return render_to_response('manage/staff.html', locals(), context_instance=RequestContext(request))
    else:
        form = StaffForm(instance=staff)
    return render_to_response('manage/staff.html', locals(), context_instance=RequestContext(request))


def delete_staff(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Staff.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=staff')

def activate_staff(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Staff.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=staff')


# -------------------------------- Section --------------------------------------- ---------------- #


def add_section(request):
    if request.method == "POST":
        form = SectionForm(request.POST, request.FILES)
        if form.is_valid():
            check=Section.objects.filter(name__iexact=request.POST.get('name'))
            if not check:
                obj=form.save(commit=False)
                obj.slug=slugify(request.POST.get('name'))
                obj.save()
                return render_to_response('manage/add_section.html', {'added':True}, context_instance=RequestContext(request))
            else:
                error= "Section type name already exist."
                form = SectionForm(request.POST)
                return render_to_response('manage/add_section.html', {'form':form}, context_instance=RequestContext(request))
        else:
            form = SectionForm(request.POST, request.FILES)
        return render_to_response('manage/add_section.html', {'form':form}, context_instance=RequestContext(request))
    
    else:
        
        form = SectionForm()
    return render_to_response('manage/add_section.html', {'form':form}, context_instance=RequestContext(request))


def edit_section(request, id=''):
    if id== '':
        id=request.GET.get('id', '')
    section = Section.objects.get(id=id)
    if request.method == "POST":
        form = SectionForm(request.POST,request.FILES, instance = section)
        if form.is_valid():
            if not has_changed(instance= section,field='name'):
                    form.save()
                    return render_to_response('manage/add_section.html', {'edit_done':True, 'id':id}, context_instance=RequestContext(request))
            else:
                check=Section.objects.filter(name__iexact=request.POST.get('name'))
                if not check:
                    form.save()
                    return render_to_response('manage/add_section.html', {'edit_done':True, 'id':id}, context_instance=RequestContext(request))
                else:
                    error= "Section name already exist"
                    form = SectionForm(request.POST)
                    return render_to_response('manage/add_section.html', {'form':form, 'edit':True, 'error':error, 'id':id}, context_instance=RequestContext(request))    
        else:
            form = SectionForm(request.POST, request.FILES)
        return render_to_response('manage/add_section.html', {'form':form, 'edit':True, 'id':id}, context_instance=RequestContext(request))
    else:
        form = SectionForm(instance= section)
    return render_to_response('manage/add_section.html', {'form':form, 'edit':True, 'id':id}, context_instance=RequestContext(request))


def delete_section(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Section.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=section')

def activate_section(request, id=''):
    
    if id == '':
        id = request.GET.get('id')
    obj = Section.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=section')

#-------------------------------------------------- Fundraiser Type --------------------------------------------------------#

def add_fundtype(request):
    if request.method == "POST":
        form = FundraiserTypeForm(request.POST, request.FILES)
        if form.is_valid():
            f1 = form.save( commit = False)
            f1.slug=slugify(request.POST.get('name'))
            f1.color = request.POST.get('color')
            f1.save()
            added = True
            return render_to_response('manage/add_fundraisetype.html', locals(), context_instance=RequestContext(request))
        else:
            form = FundraiserTypeForm(request.POST, request.FILES)
        return render_to_response('manage/add_fundraisetype.html', locals(), context_instance=RequestContext(request))
    else:
        form = FundraiserTypeForm()
    return render_to_response('manage/add_fundraisetype.html', locals(), context_instance=RequestContext(request))



def edit_fundtype(request, f_id=''):
    edit = True
    if f_id == '':
        f_id=request.GET.get('f_id')
    fund_type_obj=FundraiserType.objects.get(id=f_id)
    if request.method== "POST":
        form=FundraiserTypeForm(request.POST, request.FILES, instance = fund_type_obj)
        if form.is_valid():
            f1 = form.save(commit=False)
            f1.color = request.POST.get('color')
            f1.save()
            edit_done = True
        else:
            form=FundraiserTypeForm(request.POST, request.FILES)
            return render_to_response('manage/add_fundraisetype.html', locals(), context_instance=RequestContext(request))
    else:
        form=FundraiserTypeForm(instance = fund_type_obj)
        return render_to_response('manage/add_fundraisetype.html', locals(), context_instance=RequestContext(request))
    return render_to_response('manage/add_fundraisetype.html', locals(), context_instance=RequestContext(request))


def delete_fundtype(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = FundraiserType.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=fundraisertype')

def activate_fundtype(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = FundraiserType.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=fundraisertype')

#-------------------------------------------------- Fundraiser --------------------------------------------------------#

def add_fund(request):
    if request.method == "POST":
        form = FundraiserFormBk(request.POST, request.FILES)
        if form.is_valid():
            f=form.save(commit=False)
            created_by = request.POST.get('created_by')
            ngo_obj = NGO.objects.filter(contact_person__user__id=created_by)
            if ngo_obj:
                mes = 'User is a NGO'
                return render_to_response('manage/add_fundraise.html', locals(), context_instance=RequestContext(request))
            f.save()
            added = True
            return render_to_response('manage/add_fundraise.html', locals(), context_instance=RequestContext(request))
        else:
            form = FundraiserFormBk(request.POST, request.FILES)
        return render_to_response('manage/add_fundraise.html', locals(), context_instance=RequestContext(request))
    else:
        form = FundraiserFormBk()
    return render_to_response('manage/add_fundraise.html', locals(), context_instance=RequestContext(request))



def edit_fund(request, f_id=''):
    edit = True
    ngo_obj = ''
    if f_id == '':
        f_id=request.GET.get('f_id')
    fund_obj=Fundraiser.objects.get(id=f_id)
    if request.method== "POST":
        form=FundraiserFormBk(request.POST, request.FILES, instance = fund_obj)
        created_by = request.POST.get('created_by')
        ngo_obj = NGO.objects.filter(contact_person__user__id=created_by, active=True)
        if ngo_obj:
            mes = 'User is a NGO'
            return render_to_response('manage/add_fundraise.html', locals(), context_instance=RequestContext(request))
        if form.is_valid():
            form.save()
            edit_done = True
        else:
            form=FundraiserFormBk(request.POST, request.FILES)
            return render_to_response('manage/add_fundraise.html', locals(), context_instance=RequestContext(request))
    else:
        form=FundraiserFormBk(instance = fund_obj)
        return render_to_response('manage/add_fundraise.html', locals(), context_instance=RequestContext(request))
    return render_to_response('manage/add_fundraise.html', locals(), context_instance=RequestContext(request))


def delete_fund(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Fundraiser.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=fundraisers')

def activate_fund(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Fundraiser.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=fundraisers')

#-------------------------------------------------- Fundraiser Type Details--------------------------------------------------------#

def add_ftypedet(request):
    ftype_id = request.GET.get('ftype_id')
    if request.method == "POST":
        ftype_obj = FundraiserType.objects.get(id=ftype_id)
        form = FundraiserTypeDetailsForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save( commit = False)
            f.ftype = ftype_obj
            f.save()
            added = True
            return render_to_response('manage/add_ftypedet.html', locals(), context_instance=RequestContext(request))
        else:
            form = FundraiserTypeDetailsForm(request.POST, request.FILES)
        return render_to_response('manage/add_ftypedet.html', locals(), context_instance=RequestContext(request))
    else:
        form = FundraiserTypeDetailsForm()
    return render_to_response('manage/add_ftypedet.html', locals(), context_instance=RequestContext(request))

def edit_ftypedet(request):
    edit = True
    ftypedet_id = request.GET.get('ftypedet')
    ftypedet_obj = FundraiserType_details.objects.get(id=ftypedet_id)
    if request.method== "POST":
        form=FundraiserTypeDetailsForm(request.POST, request.FILES, instance = ftypedet_obj)
        if form.is_valid():
            form.save()
            edit_done = True
        else:
            form=FundraiserTypeDetailsForm(request.POST, request.FILES)
    else:
        form=FundraiserTypeDetailsForm(instance = ftypedet_obj)
    return render_to_response('manage/add_ftypedet.html', locals(), context_instance=RequestContext(request))

# -------------------------------- Events--------------------------------------- ---------------- #

def add_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            check = Event.objects.filter(slug__iexact = request.POST.get('slug')).exists()
            if not check:
                fundraisertype_list = request.POST.getlist('allowed_categories')
                f = form.save(commit=False)
                f.color = request.POST.get('color')
                f.save()
                for i in fundraisertype_list:
                    ft_obj = FundraiserType.objects.get(id=i)
                    f.allowed_categories.add(ft_obj)
                    f.save()
                added = True
            else:
                msg="Slug already exists"
            return render_to_response('manage/add_edit_event.html', locals(), context_instance=RequestContext(request))
        else:
            form = EventForm(request.POST, request.FILES)
        return render_to_response('manage/add_edit_event.html', locals(), context_instance=RequestContext(request))
    else:
        form = EventForm()
    return render_to_response('manage/add_edit_event.html', locals(), context_instance=RequestContext(request))



def edit_event(request):
    edit = True
    event_id=request.GET.get('event_id')
    event = Event.objects.get(id=event_id)
    if request.method== "POST":
        form=EventForm(request.POST, request.FILES ,instance = event)
        if form.is_valid():
            if not Event.objects.filter(slug__iexact = request.POST.get('slug')).exclude(id = event.id):
                fundraisertype_list = request.POST.getlist('allowed_categories')
                f = form.save(commit=False)
                f.color = request.POST.get('color')
                f.allowed_categories = fundraisertype_list
                f.save()
                edit_done = True
            else:
                msg = "Slug already exist "
                form=EventForm(request.POST)
                return render_to_response('manage/add_edit_event.html', locals(), context_instance=RequestContext(request))
        else:
            form=EventForm(request.POST)
            return render_to_response('manage/add_edit_event.html', locals(), context_instance=RequestContext(request))
    else:
        form=EventForm(instance = event)
        return render_to_response('manage/add_edit_event.html', locals(), context_instance=RequestContext(request))
    return render_to_response('manage/add_edit_event.html', locals(), context_instance=RequestContext(request))


def delete_event(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Event.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=event')

def activate_event(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Event.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=event')
# -------------------------------- Event About Us--------------------------------------- ---------------- #

def add_eventaboutus(request, eid=''):
    event = Event.objects.get(id=eid)
    if request.method == "POST":
        form = EventAboutUsForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save(commit=False)
            f.event= event
            f.save()
            added = True
            return render_to_response('manage/add_edit_eventaboutus.html', locals(), context_instance=RequestContext(request))
        else:
            form = EventAboutUsForm(request.POST, request.FILES)
        return render_to_response('manage/add_edit_eventaboutus.html', locals(), context_instance=RequestContext(request))
    else:
        form = EventAboutUsForm()
    return render_to_response('manage/add_edit_eventaboutus.html', locals(), context_instance=RequestContext(request))

def edit_eventaboutus(request, eid=''):
    edit = True
    event = Event.objects.get(id=eid)
    try:
        event_about_us = EventAboutUs.objects.get(event=event)
    except:
        pass
    if request.method == "POST":
        form = EventAboutUsForm(request.POST, request.FILES, instance=event_about_us)
        if form.is_valid():
            form.save()
            edit_done = True
            return render_to_response('manage/add_edit_eventaboutus.html', locals(), context_instance=RequestContext(request))
        else:
            form = EventAboutUsForm(request.POST, request.FILES)
        return render_to_response('manage/add_edit_eventaboutus.html', locals(), context_instance=RequestContext(request))
    else:
        form = EventAboutUsForm(instance=event_about_us)
    return render_to_response('manage/add_edit_eventaboutus.html', locals(), context_instance=RequestContext(request))

# -------------------------------- Event Contact Us--------------------------------------- ---------------- #

def add_eventcontactus(request, eid=''):
    event = Event.objects.get(id=eid)
    if request.method == "POST":
        form = EventContactUsForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save(commit=False)
            f.event= event
            f.save()
            added = True
            return render_to_response('manage/add_edit_eventcontactus.html', locals(), context_instance=RequestContext(request))
        else:
            form = EventContactUsForm(request.POST, request.FILES)
        return render_to_response('manage/add_edit_eventcontactus.html', locals(), context_instance=RequestContext(request))
    else:
        form = EventContactUsForm()
    return render_to_response('manage/add_edit_eventcontactus.html', locals(), context_instance=RequestContext(request))

def edit_eventcontactus(request, eid=''):
    edit = True
    event = Event.objects.get(id=eid)
    try:
        event_contact_us = EventContactUs.objects.get(event=event)
    except:
        pass
    if request.method == "POST":
        form = EventContactUsForm(request.POST, request.FILES, instance=event_contact_us)
        if form.is_valid():
            form.save()
            edit_done = True
            return render_to_response('manage/add_edit_eventcontactus.html', locals(), context_instance=RequestContext(request))
        else:
            form = EventContactUsForm(request.POST, request.FILES)
        return render_to_response('manage/add_edit_eventcontactus.html', locals(), context_instance=RequestContext(request))
    else:
        form = EventContactUsForm(instance=event_contact_us)
    return render_to_response('manage/add_edit_eventcontactus.html', locals(), context_instance=RequestContext(request))



# -------------------------------- Event Articles--------------------------------------- ---------------- #

def add_eventarticle(request, eid=''):
    event = Event.objects.get(id=eid)
    if request.method == "POST":
        form = EventArticleForm(request.POST, request.FILES)
        if form.is_valid():
            check = EventArticle.objects.filter(slug=slugify(request.POST.get('name')))
            if not check:
                f = form.save(commit=False)
                f.content_type = ContentType.objects.get(model__iexact = 'event')
                f.slug = slugify(request.POST.get('name'))
                f.object_id = event.id
                f.save()
                added = True
                return render_to_response('manage/add_edit_eventarticle.html', locals(), context_instance=RequestContext(request))
            else:
                error = "Name Already exists"
                return render_to_response('manage/add_edit_eventarticle.html', locals(), context_instance=RequestContext(request))
        else:
            form = EventArticleForm(request.POST, request.FILES)
        return render_to_response('manage/add_edit_eventarticle.html', locals(), context_instance=RequestContext(request))
    else:
        form = EventArticleForm()
    return render_to_response('manage/add_edit_eventarticle.html', locals(), context_instance=RequestContext(request))

def edit_eventarticle(request, eid=''):
    edit = True
    event = Event.objects.get(id=eid)
    article_id = request.GET.get('article_id')
    evntarticle = EventArticle.objects.get(id=article_id)
    if request.method == "POST":
        form = EventArticleForm(request.POST, request.FILES, instance=evntarticle)
        if form.is_valid():
            form.save()
            edit_done = True
            return render_to_response('manage/add_edit_eventarticle.html', locals(), context_instance=RequestContext(request))
        else:
            form = EventArticleForm(request.POST, request.FILES)
        return render_to_response('manage/add_edit_eventarticle.html', locals(), context_instance=RequestContext(request))
    else:
        form = EventArticleForm(instance=evntarticle)
    return render_to_response('manage/add_edit_eventarticle.html', locals(), context_instance=RequestContext(request))

def activate_eventarticle(request, eid=''):
    event = Event.objects.get(id=eid)
    article_id = request.GET.get('article_id')
    evntarticle = EventArticle.objects.get(id=article_id)
    evntarticle.active = True
    evntarticle.save()
    return HttpResponseRedirect('/manage/?key=manage-event&event_id='+str(event.id))

def deactivate_eventarticle(request, eid=''):
    event = Event.objects.get(id=eid)
    article_id = request.GET.get('article_id')
    evntarticle = EventArticle.objects.get(id=article_id)
    evntarticle.active = False
    evntarticle.save()
    return HttpResponseRedirect('/manage/?key=manage-event&event_id='+str(event.id))


# -------------------------------- Participating NGO's in Event--------------------------------------- ---------------- #

def add_ngoevent(request, eid='', slug=""):
    event = Event.objects.get(id=eid)
    if request.method == 'POST':
        if slug == "ngo":
            form = event_ngo(request.POST)
        elif slug == "corporate-table":
            form = event_corporate_tables(request.POST)
        elif slug == "contributing-hotels":
            form = event_contributing_hotels(request.POST)
        if form.is_valid():
            if slug == "ngo":
                for i in event.ngo.all():
                    event.ngo.remove(i)
                for i in request.POST.getlist('ngo'):
                    ngo=NGO.objects.get(id=i)
                    event.ngo.add(ngo)
            if slug == "corporate-table":
                for i in event.corporate_tables.all():
                    event.corporate_tables.remove(i)
                for i in request.POST.getlist('corporate_tables'):
                    corporate_tables=Corporate_Tables.objects.get(id=i)
                    event.corporate_tables.add(corporate_tables)
            if slug == "contributing-hotels":
                for i in event.contributing_hotels.all():
                    event.contributing_hotels.remove(i)
                for i in request.POST.getlist('contributing_hotels'):
                    contributing_hotels=Contributing_Hotels.objects.get(id=i)
                    event.contributing_hotels.add(contributing_hotels)
            added = True
            return render_to_response('manage/add_ngoevent.html', locals(), context_instance=RequestContext(request))
        else:
            return render_to_response('manage/add_ngoevent.html', locals(), context_instance=RequestContext(request))
    else:
        if slug == "ngo":
            form = event_ngo(initial={'ngo':event.ngo.all()})
        elif slug == "corporate-table":
            form = event_corporate_tables(initial={'corporate_tables':event.corporate_tables.all()})
        elif slug == "contributing-hotels":
            form = event_contributing_hotels(initial={'contributing_hotels':event.contributing_hotels.all()})
    return render_to_response('manage/add_ngoevent.html', locals(), context_instance=RequestContext(request))


def edit_ngoevent(request, eid='', slug=""):
    edit = True
    event = Event.objects.get(id=eid)
    if request.method == 'POST':
        if slug == "ngo":
            form = event_ngo(request.POST)
        elif slug == "corporate-care-team-20":
            form = event_fundraisercct20form(request.POST)
        elif slug == "corporate-table":
            form = event_corporate_tables(request.POST)
        elif slug == "contributing-hotels":
            form = event_contributing_hotels(request.POST)
        if form.is_valid():
            if slug == "ngo":
                for n in event.ngo.all():
                    event.ngo.remove(n)
                for i in request.POST.getlist('ngo'):
                    ngo=NGO.objects.get(id=i)
                    event.ngo.add(ngo)
            if slug == "corporate-table":
                for i in event.corporate_tables.all():
                    event.corporate_tables.remove(i)
                for i in request.POST.getlist('corporate_tables'):
                    corporate_tables=Corporate_Tables.objects.get(id=i)
                    event.corporate_tables.add(corporate_tables)
            if slug == "contributing-hotels":
                for i in event.contributing_hotels.all():
                    event.contributing_hotels.remove(i)
                for i in request.POST.getlist('contributing_hotels'):
                    contributing_hotels=Contributing_Hotels.objects.get(id=i)
                    event.contributing_hotels.add(contributing_hotels)
            edit_done = True
            return render_to_response('manage/add_ngoevent.html', locals(),context_instance=RequestContext(request))
        else:
            return render_to_response('manage/add_ngoevent.html', locals(),context_instance=RequestContext(request))
    else:
        if slug == "ngo":
            form = event_ngo(initial={'ngo':event.ngo.all()})
        elif slug == "corporate-table":
            form = event_corporate_tables(initial={'corporate_tables':event.corporate_tables.all()})
        elif slug == "contributing-hotels":
            form = event_contributing_hotels(initial={'contributing_hotels':event.contributing_hotels.all()})
    return render_to_response('manage/add_ngoevent.html', locals(),context_instance=RequestContext(request))



# -------------------------------- Participating Fundraiser's in Event--------------------------------------- ---------------- #

def add_fundevent(request, eid='', ftid=""):
    event = Event.objects.get(id=eid)
    f = get_ftype_form(ftid)
    form = f
    if request.method == 'POST':
        form = f(request.POST)
        if form.is_valid():
            for i in event.fundraisers.filter(fundraiser_type__id=ftid):
                event.fundraisers.remove(i)
            for i in request.POST.getlist('fundraiser'):
                ft_obj=Fundraiser.objects.get(id=i)
                event.fundraisers.add(ft_obj)
            added = True
            return render_to_response('manage/add_fundraiser_event.html', locals(), context_instance=RequestContext(request))
        else:
            return render_to_response('manage/add_fundraiser_event.html', locals(), context_instance=RequestContext(request))
    else:
        form = f(initial={'fundraiser':event.fundraisers.all()})
    return render_to_response('manage/add_fundraiser_event.html', locals(), context_instance=RequestContext(request))


def edit_fundevent(request, eid='', ftid=""):
    edit = True
    event = Event.objects.get(id=eid)
    f = get_ftype_form(ftid)
    if request.method == 'POST':
        form = f(request.POST)
        if form.is_valid():
            for i in event.fundraisers.filter(fundraiser_type__id=ftid):
                event.fundraisers.remove(i)
            for i in request.POST.getlist('fundraiser'):
                ft_obj=Fundraiser.objects.get(id=i)
                event.fundraisers.add(ft_obj)
            edit_done = True
            return render_to_response('manage/add_fundraiser_event.html', locals(),context_instance=RequestContext(request))
        else:
            return render_to_response('manage/add_fundraiser_event.html', locals(),context_instance=RequestContext(request))
    else:
        form = f(initial={'fundraiser':event.fundraisers.all()})
    return render_to_response('manage/add_fundraiser_event.html', locals(),context_instance=RequestContext(request))


# -------------------------------- Participating Display Front End--------------------------------------- ---------------- #

def add_displayfundevent(request, eid=''):
    event = Event.objects.get(id=eid)
    f = get_display_ftype_form(eid)
    form = f
    if request.method == 'POST':
        form = f(request.POST, request.FILES)
        if form.is_valid():
            fundraiser_type_id = request.POST.getlist('fundraiser_type')
            event.display_name = request.POST.get('name')
            for i in fundraiser_type_id:
                ftype = FundraiserType.objects.get(id=i)
                event.display.add(ftype)
            event.save()
            added = True
            return render_to_response('manage/add_display_fund_type.html', locals(), context_instance=RequestContext(request))
        else:
            return render_to_response('manage/add_display_fund_type.html', locals(), context_instance=RequestContext(request))
    else:
        form = f(initial={'fundraiser_type':event.display.all(), 'name':event.display_name})
    return render_to_response('manage/add_display_fund_type.html', locals(), context_instance=RequestContext(request))


def edit_displayfundevent(request, eid=''):
    edit = True
    event = Event.objects.get(id=eid)
    f = get_display_ftype_form(eid)
    if request.method == 'POST':
        form = f(request.POST)
        if form.is_valid():
            fundraiser_type_id = request.POST.getlist('fundraiser_type')
            event.display_name = request.POST.get('name')
            event.display=fundraiser_type_id
            event.save()
            edit_done = True
            return render_to_response('manage/add_display_fund_type.html', locals(),context_instance=RequestContext(request))
        else:
            return render_to_response('manage/add_display_fund_type.html', locals(),context_instance=RequestContext(request))
    else:
        form = f(initial={'fundraiser_type':event.display.all(), 'name':event.display_name})
    return render_to_response('manage/add_display_fund_type.html', locals(),context_instance=RequestContext(request))

# -------------------------------- Participating Display Scroller--------------------------------------- ---------------- #

def add_displayonefundevent(request, eid=''):
    event = Event.objects.get(id=eid)
    f = get_display_ftype_form(eid)
    form = f
    if request.method == 'POST':
        form = f(request.POST, request.FILES)
        if form.is_valid():
            fundraiser_type_id = request.POST.getlist('fundraiser_type')
            event.display_one_name = request.POST.get('name')
            for i in fundraiser_type_id:
                ftype = FundraiserType.objects.get(id=i)
                event.display_one.add(ftype)
            event.save()
            added = True
            return render_to_response('manage/add_display_scroll.html', locals(), context_instance=RequestContext(request))
        else:
            return render_to_response('manage/add_display_scroll.html', locals(), context_instance=RequestContext(request))
    else:
        form = f(initial={'fundraiser_type':event.display_one.all(), 'name':event.display_one_name})
    return render_to_response('manage/add_display_scroll.html', locals(), context_instance=RequestContext(request))


def edit_displayonefundevent(request, eid=''):
    edit = True
    event = Event.objects.get(id=eid)
    f = get_display_ftype_form(eid)
    if request.method == 'POST':
        form = f(request.POST)
        if form.is_valid():
            fundraiser_type_id = request.POST.getlist('fundraiser_type')
            event.display_one_name = request.POST.get('name')
            event.display_one=fundraiser_type_id
            event.save()
            edit_done = True
            return render_to_response('manage/add_display_scroll.html', locals(),context_instance=RequestContext(request))
        else:
            return render_to_response('manage/add_display_scroll.html', locals(),context_instance=RequestContext(request))
    else:
        form = f(initial={'fundraiser_type':event.display_one.all(), 'name':event.display_one_name})
    return render_to_response('manage/add_display_scroll.html', locals(),context_instance=RequestContext(request))

# -------------------------------- Event Overview--------------------------------------- ---------------- #
def add_eventoverview(request, eid=''):
    event = Event.objects.get(id=eid)
    if request.method == "POST":
        form = EventOverviewForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save(commit=False)
            f.name = 'Overview'
            f.content_type = ContentType.objects.get(model__iexact = 'event')
            f.slug = 'overview'
            f.object_id = event.id
            f.save()
            added = True
            return render_to_response('manage/add_edit_eventoverview.html', locals(), context_instance=RequestContext(request))
        else:
            form = EventOverviewForm(request.POST, request.FILES)
        return render_to_response('manage/add_edit_eventoverview.html', locals(), context_instance=RequestContext(request))
    else:
        form = EventOverviewForm()
    return render_to_response('manage/add_edit_eventoverview.html', locals(), context_instance=RequestContext(request))

def edit_eventoverview(request, eid=''):
    edit = True
    event = Event.objects.get(id=eid)
    article_id = request.GET.get('article_id')
    evntarticle = EventArticle.objects.get(id=article_id)
    if request.method == "POST":
        form = EventOverviewForm(request.POST, request.FILES, instance=evntarticle)
        if form.is_valid():
            form.save()
            edit_done = True
            return render_to_response('manage/add_edit_eventoverview.html', locals(), context_instance=RequestContext(request))
        else:
            form = EventOverviewForm(request.POST, request.FILES)
        return render_to_response('manage/add_edit_eventoverview.html', locals(), context_instance=RequestContext(request))
    else:
        form = EventOverviewForm(instance=evntarticle)
    return render_to_response('manage/add_edit_eventoverview.html', locals(), context_instance=RequestContext(request))

# -------------------------------- Event Banners--------------------------------------- ---------------- #

def add_eventbanners(request, eid=''):
    event = Event.objects.get(id=eid)
    if request.method == "POST":
        form = EventBannerForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save(commit=False)
            f.content_type = ContentType.objects.get(model__iexact = 'event')
            f.object_id = event.id
            f.save()
            added = True
            return render_to_response('manage/add_edit_eventbanner.html', locals(), context_instance=RequestContext(request))
        else:
            form = EventBannerForm(request.POST, request.FILES)
        return render_to_response('manage/add_edit_eventbanner.html', locals(), context_instance=RequestContext(request))
    else:
        form = EventBannerForm()
    return render_to_response('manage/add_edit_eventbanner.html', locals(), context_instance=RequestContext(request))

def edit_eventbanners(request, eid=''):
    edit = True
    event = Event.objects.get(id=eid)
    banner_id = request.GET.get('banner_id')
    evntbanner = EventBanners.objects.get(id=banner_id)
    if request.method == "POST":
        form = EventBannerForm(request.POST, request.FILES, instance=evntbanner)
        if form.is_valid():
            form.save()
            edit_done = True
            return render_to_response('manage/add_edit_eventbanner.html', locals(), context_instance=RequestContext(request))
        else:
            form = EventBannerForm(request.POST, request.FILES)
        return render_to_response('manage/add_edit_eventbanner.html', locals(), context_instance=RequestContext(request))
    else:
        form = EventBannerForm(instance=evntbanner)
    return render_to_response('manage/add_edit_eventbanner.html', locals(), context_instance=RequestContext(request))

#-------------------------------------------------- Contact Us --------------------------------------------------------#

def add_contactus(request):
    if request.method == "POST":
        form = ContactUsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            added = True
            return render_to_response('manage/add_contactus.html', locals(), context_instance=RequestContext(request))
        else:
            form = ContactUsForm(request.POST, request.FILES)
        return render_to_response('manage/add_contactus.html', locals(), context_instance=RequestContext(request))
    else:
        form = ContactUsForm()
    return render_to_response('manage/add_contactus.html', locals(), context_instance=RequestContext(request))



def edit_contactus(request, contactus_id=''):
    edit = True
    if contactus_id == '':
        contactus_id=request.GET.get('contactus_id')
    conatct_us_obj=Contactus.objects.get(id=contactus_id)
    if request.method== "POST":
        form=ContactUsForm(request.POST, request.FILES, instance = conatct_us_obj)
        if form.is_valid():
            form.save()
            edit_done = True
        else:
            form=ContactUsForm(request.POST, request.FILES)
            return render_to_response('manage/add_contactus.html', locals(), context_instance=RequestContext(request))
    else:
        form=ContactUsForm(instance = conatct_us_obj)
    return render_to_response('manage/add_contactus.html', locals(), context_instance=RequestContext(request))

#----------------------------------ADDress ----------------------------------------------#

def add_address(request):
    key = request.GET.get('key')
    address_id = request.GET.get('address_id')
    for_model = request.GET.get('for_model')
    if request.method== "POST":
        form=AddressForm(request.POST,request.FILES)
        if form.is_valid():
            obj= form.save(commit=False)
            obj.content_type = ContentType.objects.get(name__iexact = for_model)
            obj.object_id = address_id
            obj.save()
            added = True
            return render_to_response('manage/add_address.html', locals(), context_instance=RequestContext(request))
        else:
            form=AddressForm(request.POST,request.FILES)
        return render_to_response('manage/add_address.html', locals(), context_instance=RequestContext(request))
    else:
        form=AddressForm()
    return render_to_response('manage/add_address.html', locals(), context_instance=RequestContext(request))


def edit_address(request, address_id=''):
    edit = True
    if address_id == '':
        address_id = request.GET.get('address_id')
    for_model = request.GET.get('for_model')
    address_obj=Address.objects.get(id=address_id)
    if request.method== "POST":
        form=AddressForm(request.POST,request.FILES,instance=address_obj)
        if form.is_valid():
            form.save()
            edit_done = True
            return render_to_response('manage/add_address.html', locals(), context_instance=RequestContext(request))
        else:
            form=AddressForm(request.POST,request.FILES)
        return render_to_response('manage/add_address.html', locals(), context_instance=RequestContext(request))
    else:
        form=AddressForm(instance=address_obj)
    return render_to_response('manage/add_address.html', locals(), context_instance=RequestContext(request))

# -------------------------------- Duplicate Corporates--------------------------------------- ---------------- #

def add_duplicate_corporates(request):
    if request.method == "POST":
        form = Duplicate_CorporatesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            added = True
            return render_to_response('manage/add_duplicate_corporate.html', locals(), context_instance=RequestContext(request))
        else:
            form = Duplicate_CorporatesForm(request.POST, request.FILES)
        return render_to_response('manage/add_duplicate_corporate.html', locals(), context_instance=RequestContext(request))
    else:
        form = Duplicate_CorporatesForm()
    return render_to_response('manage/add_duplicate_corporate.html', locals(), context_instance=RequestContext(request))


def edit_duplicate_corporates(request):
    edit = True
    dup_crp_id=request.GET.get('id')
    dup_crp=Duplicate_Corporates.objects.get(id=dup_crp_id)
    if request.method== "POST":
        form=Duplicate_CorporatesForm(request.POST,instance = dup_crp)
        if form.is_valid():
            form.save()
            edit_done = True
        else:
            form=Duplicate_CorporatesForm(request.POST)
            return render_to_response('manage/add_duplicate_corporate.html', locals(), context_instance=RequestContext(request))
    else:
        form=Duplicate_CorporatesForm(instance = dup_crp)
        return render_to_response('manage/add_duplicate_corporate.html', locals(), context_instance=RequestContext(request))
    return render_to_response('manage/add_duplicate_corporate.html', locals(), context_instance=RequestContext(request))


def delete_duplicate_corporates(request, id=''):
    if id == '':
        id = request.GET.get('id')
    event_id = request.GET.get('event_id')
    obj = Duplicate_Corporates.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=manage-event&event_id='+str(event_id))

def activate_duplicate_corporates(request, id=''):
    if id == '':
        id = request.GET.get('id')
    obj = Duplicate_Corporates.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=duplicate-corporates')

