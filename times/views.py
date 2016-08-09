from django.shortcuts import render
from django.shortcuts import render, render_to_response
from django.core.paginator  import Paginator,InvalidPage, EmptyPage
from django.http import HttpResponse,HttpResponseRedirect
from times.models import AddTime
from times.models import AddTime
from forms import *
from client.models import Client
from django.core.context_processors import csrf
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.template.defaultfilters import slugify
from tasks.models import Tasks
from datetime import *
from projects.models import *
from django.contrib.auth.decorators import login_required
todays = datetime.date.today()
today_date = date.today()
# Create your views here.

import datetime
@login_required(login_url="/login/")
def addtimes(request):
    key = ''
    task_id = request.GET.get('task_id')

    if task_id:
        try:
            task_obj = Tasks.objects.get(id=task_id)
            client_obj = task_obj.client
            project_obj = task_obj.project
        except:
            pass
    tasks = Tasks.objects.filter(status=1)
    form = Time_Form(request.user.pk)
    user_id = request.user.id
    user_id2 = UserProfile.objects.get(user__id=user_id)
    today = today_date
    error = ''
    msg = ''
    nam = ''
    x = ''
    f = ''
    if request.method == 'POST':
        form = form(request.POST)
        name = request.POST.get('name', '')
        client_id = request.POST.get('client', '')
        project_id = request.POST.get('project', '')
        if form.is_valid():
            f = form.save(commit=False)
            if client_id:
                client_obj = Client.objects.get(id=client_id)
                f.client = client_obj
            if project_id:
                project_obj = Project.objects.get(id=project_id)
                f.project = project_obj
            f.slug=name
            f.save()
            msg = "successfully saved"
            return HttpResponseRedirect("/times/")
        else:
            error = "form error"
    return render(request,"times/tim.html", locals(), context_instance=RequestContext(request))

@login_required(login_url="/login/")
def edittimes(request, id_edit):
    msg = ''
    key = 'edit'
    time_obj = AddTime.objects.get(id=id_edit)
    clnt = time_obj.client
    client = Client.objects.all()
    proj = time_obj.project
    project = Project.objects.all()
    f = Time_Form(request.user.pk)
    form = f(initial={'client': time_obj.client.id, 'project': time_obj.project.id, 'module': time_obj.module.id, 'person': time_obj.person.id, 'times': time_obj.times, 'tasks': time_obj.tasks if time_obj.tasks else None, 'worktype': time_obj.worktype.id, 'date': time_obj.date, 'description': time_obj.description})
    if request.method == 'POST':
        form = f(request.POST, )
        if form.is_valid():
            client = request.POST.get('client', '')
            project = request.POST.get('project', '')
            person = request.POST.get('person', '')
            times = request.POST.get('times', '')
            tasks = request.POST.get('tasks', '')
            date = request.POST.get('date', '')
            description = request.POST.get('description', '')
            module = request.POST.get('module', '')
            billable = request.POST.get('billable')
            worktype = request.POST.get('worktype', '')
            if client:
                client_obj = Client.objects.get(id=client)
            if project:
                project_obj = Project.objects.get(id=project)
            time_obj.client = client_obj
            time_obj.project = project_obj
            person_obj = UserProfile.objects.get(id=person)
            time_obj.person = person_obj
            time_obj.date = date
            module_obj = Modules.objects.get(id=module)
            time_obj.module = module_obj
            worktype_obj = Work_Type.objects.get(id=worktype)
            time_obj.worktype = worktype_obj
            if tasks:
                task_obj = Tasks.objects.get(id=tasks)
                time_obj.tasks = task_obj
            else:
                time_obj.tasks = None
            time_obj.times = times
            time_obj.description = description
            time_obj.billable = billable
            time_obj.save()
            edit_done = True
            msg = "edited successfully"
            success = True
            return HttpResponseRedirect("/times/")
        else:
             msg = 'Invalid form'
    return render(request, "times/tim.html", locals())


@login_required(login_url="/login/")
def addmtimes(request):
    f = Time_Form(int(request.user.pk))
    form = f()
    subform = f(prefix="tim")
    subbform = f(prefix="tims")
    error = ''
    msg = ''
    nam = ''
    x = ''
    f = ''
    s = ''
    ss = ''
    messages = ''
    if request.method == 'POST':
        form = f(request.POST or None)
        subform = f(request.POST or None, prefix="tim")
        subbform = f(request.POST or None, prefix="tims")
        #form_description = request.POST('description','')
        #subform_description = request.POST('description','')
        #subbform_description = request.POST('description','')
        if form.is_valid() and subform.is_valid() and subbform.is_valid():
            f = form.save(commit=False)
            f.save()
            s = subform.save(commit=False)
            s.save()
            ss = subbform.save(commit=False)
            ss.save()
            msg = "successfully saved"
            return HttpResponseRedirect("/times/")
        else:
            error = "form error"
    return render(request,"times/mtim.html", locals(), context_instance=RequestContext(request))


@login_required(login_url="/login/")
def times_home(request):
    today = todays
    date = datetime.date.today()
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(7)
    previous_week_start_date = start_week - datetime.timedelta(7)
    next_week_start_date = start_week + datetime.timedelta(7)
    previous_week_end_date = previous_week_start_date + datetime.timedelta(5)
    day_list =  [start_week + datetime.timedelta(days=x) for x in range(0,6)]
    days_list = [i.strftime("%A") for i in day_list]
    days_list_date = [[i.strftime("%A"), i.strftime("%y-%m-%d")] for i in day_list]
    user = request.user.id
    userprofile_obj = UserProfile.objects.get(user=user)
    if userprofile_obj.access_level == '1':
        timess = AddTime.objects.filter(date__range=[start_week, end_week])
    else:
        timess = AddTime.objects.filter(person=userprofile_obj, date__range=[start_week, end_week], status_view=0)
    times = timess
    #monday = timess.get(person=userprofile_obj, date=start_date)
    return render(request, "times/times-home.html", locals())


@login_required(login_url="/login/")
def manage_time_sheets(request, task=None):
    if task == "submit":
        id_submit = request.GET.get('id')
        time_obj = AddTime.objects.get(id=id_submit)
        time_obj.status_view = 1
        time_obj.save()
        msg = "Time sheet submitted"
        return HttpResponseRedirect("/times/manage/timesheets/")
    elif task == "approve":
        id_approve = request.GET.get('id')
        time_obj = AddTime.objects.get(id=id_approve)
        time_obj.status_view = 2
        time_obj.save()
        msg = "Time sheet approved"
        return HttpResponseRedirect("/times/manage/timesheets/")
    elif task == "reject":
        id_reject = request.GET.get('id')
        time_obj = AddTime.objects.get(id=id_reject)
        time_obj.status_view = 3
        time_obj.save()
        msg = "Time sheet rejected"
        return HttpResponseRedirect("/times/manage/timesheets/")
    #else:
        #return HttpResponseRedirect("/times/manage/timesheets/")
    return render(request, "times/manage_time.html", locals())


@login_required(login_url="/login/")
def times_sheet(request):
    user = request.user
    userprofile_obj = UserProfile.objects.get(user=user.id)
    date = datetime.date.today()
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(7)
    previous_week_start_date = start_week - datetime.timedelta(7)
    previous_week_end_date = previous_week_start_date + datetime.timedelta(5)
    timess = AddTime.objects.filter(person=userprofile_obj, date__range=[previous_week_start_date, previous_week_end_date], status_view=0)
    times_sheet_obj = Time_Sheets.objects.create(person=userprofile_obj, start_date=previous_week_start_date, end_date=previous_week_end_date, billable=True)
    times_sheet_obj.time_sheet = []
    for i in timess:
        times_sheet_obj.time_sheet.add(i)
        times_sheet_obj.save()
    for i in timess:
        i.status_view = 1
        i.save()
    return HttpResponseRedirect("/times/")

def manage_timesheets(request):

    userprofile_list = UserProfile.objects.all()
    user_obj = request.user.id
    times_person_obj = AddTime.objects.filter(person__id=user_obj)
    times_view_obj = times_person_obj.filter(status_view='0')
    times_submitted = times_person_obj.filter(status_view='1')
    times_approve = times_person_obj.filter(status_view='2')
    times_reject = times_person_obj.filter(status_view='3')
    return render(request,"times/manage-timesheets.html", locals())


@login_required(login_url="/login/")
def current_week(request):

    times = AddTime.objects.all()
    id_submit = request.GET.get('id_submit')
    curentweek_obj = AddTime.objects.get(id=id_submit)
    curentweek_obj.status_view = 2
    curentweek_obj.save()
    current_week = AddTime.objects.filter(status_view=2)
    #e=AddTime.objects.filter(status_view=2)
    return render(request, "times/manage_time.html", locals())

import datetime
@login_required(login_url="/login/")
def weekly_time_sheets(request):
    """  This is to display time sheets based on the weeks """

    key = 'week'
    user = request.user
    date = datetime.datetime.now().date()
    current_week_start_date = date - datetime.timedelta(date.weekday())
    next_week_start_date = current_week_start_date + datetime.timedelta(7)
    previous_week_start_date = current_week_start_date - datetime.timedelta(7)
    previous_week_end_date = previous_week_start_date + datetime.timedelta(5)
    day_list =  [current_week_start_date + datetime.timedelta(days=x) for x in range(0,6)]
    days_list = [i.strftime("%A") for i in day_list]
    days_list_date = [[i.strftime("%A"), i.strftime("%y-%m-%d")] for i in day_list]
    userprofile_obj = UserProfile.objects.get(user=user.id)
    #times_sheets = Time_Sheets.objects.filter(person=userprofile_obj)
    previous_week = request.POST.get('previous_week','')
    next_week = request.POST.get('next_week','')
    times_sheets = AddTime.objects.filter(date__range=[current_week_start_date, next_week_start_date])

    if previous_week:
        d = previous_week.split('-')
        previous_week_start_date = datetime.date(int(d[0]), int(d[1]), int(d[2])) - datetime.timedelta(7)
        next_week_start_date = previous_week_start_date + datetime.timedelta(7)
    if next_week:
        nd = next_week.split('-')
        next_week_start_date = datetime.date(int(nd[0]),int(nd[1]), int(nd[2])) + datetime.timedelta(7)
        previous_week_start_date = next_week_start_date - datetime.timedelta(7)
    if previous_week_start_date:
        times_sheets = AddTime.objects.filter(date__range=[previous_week_start_date, next_week_start_date])
    if next_week:
        times_sheets = AddTime.objects.filter(date__range=[previous_week_start_date, next_week_start_date])
    time = times_sheets
    return render(request, "times/times-home.html",locals())


@login_required(login_url="/login/")
def activetimer(request):

    times = AddTime.objects.all()
    task = Tasks.objects.values('title').distinct()
    return render(request, "times/active_timers.html", locals())



@login_required(login_url="/login/")
def missingtime(request):

    date=request.GET.get('date', '')
    if date:
        times = AddTime.objects.filterQ(date__gte=date), Q(date__lte=date)
    return render(request, "times/missing_timesheets.html", locals())


@login_required(login_url="/login/")
def whg(request):

    times = AddTime.objects.all()
    return render(request, "times/weekly_hour_graph.html", locals())


@login_required(login_url="/login/")
def sub(request):

    times = AddTime.objects.all()
    return render(request, "times/submitted.html", locals())


@login_required(login_url="/login/")
def timeview(request):

    disp = request.GET.get('id')
    tim = AddTime.objects.get(id=disp)
    return render(request, "times/time_view.html", locals())


@login_required(login_url="/login/")
def deletetimes(request, id_delete):

    p = AddTime.objects.get(id=id_delete)
    p.delete()
    return HttpResponseRedirect("/times/")


