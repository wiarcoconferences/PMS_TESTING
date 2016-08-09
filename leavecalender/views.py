from django.shortcuts import render
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from leavecalender.models import *
from leavecalender.forms import *
from django.contrib.auth.decorators import login_required
from people.models import *
from datetime import *
todays = datetime.today()



def calender_details(request, task=None):
    msg = ''
    Success = False
    if task == 'add':
        form = LeaveCalenderForm()
        if request.method == "POST":
            form = LeaveCalenderForm(request.POST, request.FILES)
            name = request.POST.get('name', '')
            description = request.POST.get('description', '')
            date = request.POST.get('date', '')
            image = request.FILES.get('image')
            optional = request.POST.get('optional','')
            if form.is_valid():
                if LeaveCalender.objects.filter(name=name):
                    msg = "Name already exisits"
                else:
                    leavecalender = LeaveCalender.objects.create(name=name, description=description, date=date, image=image, optional=optional )
                    added = True
                    success = True
                    return HttpResponseRedirect('/leavecalender/')

    elif task == "edit":
        id_edit = request.GET.get('id')
        leavecalenderobj = LeaveCalender.objects.get(id=id_edit)
        form = LeaveCalenderForm(initial={'name': leavecalenderobj.name, 'description': leavecalenderobj.description, 'date':leavecalenderobj.date, 'image': leavecalenderobj.image, 'optional': leavecalenderobj.optional})
        if request.method == "POST":
            form = LeaveCalenderForm(request.POST, request.FILES)
            if form.is_valid():
                if LeaveCalender.objects.filter(name=request.POST.get('name')).exclude(id=leavecalenderobj.id):
                    msg = 'Name already exist.'
                    return render(request, "mastermodule/modules.html", locals())
                else:
                    name = request.POST.get('name')
                    description = request.POST.get('description')
                    date = request.POST.get('date')
                    image = request.FILES.get('image')
                    optional = request.POST.get('optional')
                    leavecalenderobj.name = name
                    leavecalenderobj.description = description
                    leavecalenderobj.date = date
                    leavecalenderobj.image = image
                    leavecalenderobj.optional = optional
                    leavecalenderobj.save()
                    added = True
                    success = True
                    msg = 'LeaveCalender added Successfully'
                    return HttpResponseRedirect("/leavecalender/")

    elif task == "delete":
        id_delete = request.GET.get('id')
        leavecalenderobj = LeaveCalender.objects.get(id=id_delete)
        leavecalenderobj.active = 0
        leavecalenderobj.save()
        success = True
        return HttpResponseRedirect("/leavecalender/?key=view")

    elif task == "active":
        id_active = request.GET.get('id')
        leavecalenderobj = LeaveCalender.objects.get(id=id_active)
        leavecalenderobj.active = 2
        leavecalenderobj.save()
        success = True
        return HttpResponseRedirect("/leavecalender/?key=view")
    return render(request, "leavecalender/leavecaleneder-add.html", locals())

def clander_list(request):
    key = request.GET.get('key')
    if key == 'view':
        calender_list = LeaveCalender.objects.all().order_by('date')
        today_date = todays
        return render(request, "leavecalender/leavecalender-list.html", locals())
    calender_list = LeaveCalender.objects.filter(optional="No", active=2).order_by('date')
    oc_list = LeaveCalender.objects.filter(optional="Yes", active=2).order_by('date')
    today_date = todays
    return render(request, "leavecalender/leavecalender-list.html", locals())


def resource_calender_details(request, task=None):
    user = request.user.id
    userprofile = UserProfile.objects.get(user__id=user)
    if userprofile.access_level == '1':
        user_profile = UserProfile.objects.all()
    else:
        userprofile = UserProfile.objects.get(user__id=user)
    if task == 'add':
        form = Resource_LeaveCalenderForm()
        if request.method == "POST":
            form = Resource_LeaveCalenderForm(request.POST)
            person = request.POST.get('person')
            description = request.POST.get('description', '')
            start_date = request.POST.get('start_date', '')
            end_date = request.POST.get('end_date','')
            if form.is_valid():
                if person:
                    personobj = UserProfile.objects.get(id = int(person))
                    leavecalender_obj = Resource_LeaveCalender.objects.create(description=description, start_date=start_date, end_date = end_date, person=personobj)
                    leavecalender_obj.save()
                added = True
                success = True
                return HttpResponseRedirect('/resource/leavecalender/')
            else:
                msg = "Please check the form"
    elif task == "edit":
        id_edit = request.GET.get('id')
        leavecalenderobj = Resource_LeaveCalender.objects.get(id=id_edit)
        if leavecalenderobj.person:
            personobj = UserProfile.objects.get(id=leavecalenderobj.person.id)
        form = Resource_LeaveCalenderForm(initial={'person': leavecalenderobj.person, 'description': leavecalenderobj.description, 'start_date':leavecalenderobj.start_date, 'end_date': leavecalenderobj.end_date})
        if request.method == "POST":
            form = LeaveCalenderForm(request.POST, request.FILES)
            if form.is_valid():
                if Resource_LeaveCalender.objects.filter(name=request.POST.get('name')).exclude(id=leavecalenderobj.id):
                    msg = 'Name already exist.'
                    return render(request, "mastermodule/modules.html", locals())
                else:
                    person = request.POST.get('person','')
                    description = request.POST.get('description','')
                    start_date = request.POST.get('start_date')
                    end_date = request.POST.get('end_date')
                    leavecalenderobj.person = person
                    leavecalenderobj.description = description
                    leavecalenderobj.start_date = start_date
                    leavecalenderobj.end_date = end_date
                    leavecalenderobj.save()
                    added = True
                    success = True
                    msg = 'LeaveCalender added Successfully'
                    return HttpResponseRedirect("/resource/leavecalender/")

    elif task == "delete":
        id_delete = request.GET.get('id')
        leavecalenderobj = Resource_LeaveCalender.objects.get(id=id_delete)
        leavecalenderobj.active = 0
        leavecalenderobj.save()
        success = True
        return HttpResponseRedirect("/resource/leavecalender/")

    elif task == "active":
        id_active = request.GET.get('id')
        leavecalenderobj = Resource_LeaveCalender.objects.get(id=id_active)
        leavecalenderobj.active = 2
        leavecalenderobj.save()
        success = True
        return HttpResponseRedirect("/resource/leavecalender/")
    return render(request, "leavecalender/resource-leavecalender-add.html", locals())


def resource_leave_calender_list(request):
    
    key = request.GET.get('key')
    if key == 'view':
        calender_list = Resource_LeaveCalender.objects.all().order_by('start_date')
        today_date = todays
        return render(request, "leavecalender/resource-leavecalender-list.html", locals())
    user = request.user.id
    userprofile = UserProfile.objects.get(user__id=user)
    if userprofile.access_level == '1':
        calender_lists = Resource_LeaveCalender.objects.all()
    else:
        calender_lists = Resource_LeaveCalender.objects.filter(person__id=userprofile.id)
    today_date = todays
    #calender_lists = Resource_LeaveCalender.objects.all()
    return render(request, "leavecalender/resource-leavecalender-list.html", locals())
