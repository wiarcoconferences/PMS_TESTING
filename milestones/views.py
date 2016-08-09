from django.shortcuts import render
from django.shortcuts import render, render_to_response
from django.core.paginator  import Paginator,InvalidPage, EmptyPage
from django.http import HttpResponse,HttpResponseRedirect
from milestones.models import Milestone
from milestones import *
from tasks.models import Tasks
from client.models import Client
from forms import *
from projects.models import *
from django.core.context_processors import csrf
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.template.defaultfilters import slugify
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from datetime import *
from documents.models import *
from django.contrib.comments import Comment
from mastermodule.models import *
from django.contrib.sites.models import Site
# Create your views here.


def view(request, id_disp):
#    disp = request.GET.get('id')
    mil_obj = Milestone.objects.get(id=id_disp)
    #tk = Tasks.objects.get(id=id_disp)
    tasks = Tasks.objects.filter(milestone=mil_obj)

    documents = Milestone_Document.objects.all()
    return render(request, "milestones/milestone_view.html", locals())

import datetime
@login_required(login_url="/login/")
def milestone_view(request, id_disp):
    todays = datetime.date.today()
    mil_obj = Milestone.objects.get(id=(id_disp))
    cont_type = ContentType.objects.get_for_model(mil_obj)
    news_feed = Recently_Viewed.objects.create(user = request.user, content_type = cont_type, object_id = mil_obj.id,)
    task_list = Tasks.objects.filter(milestone = mil_obj).order_by('id')
    #task_list = Tasks.objects.all()
    #documents = Document.objects.filter(milestone = mil_obj)
    #docs = Document.objects.filter(content_type = content_type, objects_id = mil_obj.id )
    #cont_type = ContentType.objects.get_for_model(mil_obj)
    #comment = Comment.objects.filter(content_type = cont_type, object_pk = mil_obj.id, is_public = True)
    content_type = ContentType.objects.get_for_model(mil_obj)
    comment = Comment.objects.filter(content_type = content_type, \
    object_pk = mil_obj.pk, is_public = True)
#    doc = Document.objects.filter(content_type = content_type, objects_id = mil_obj.pk )

    return render(request, "milestones/milestone_view.html", locals())


@login_required(login_url="/login/")
def wide_view(request):
    wid = Milestone.objects.all()
    widtask = Tasks.objects.all()
    return render(request, "milestones/wide_view.html", locals())


import datetime
@login_required(login_url="/login/")
def overdueview(request):
    peoples = UserProfile.objects.all()
    todays = datetime.date.today()
    overdue_list = Milestone.objects.filter(due_date__lt=todays, status=False, owned_by__user=request.user)
    return _filter_function(request, overdue_list)


@login_required(login_url="/login/")
def addmilestone(request, task=None, id=None):
    f = Milestone_Form(request.user.pk)
    form = f
    error = ''
    todays = datetime.date.today()+timedelta(days=7)
    msg = ''
    nam = ''
    x = ''
    f = ''
    user_id=request.user.id
    user_id2 = UserProfile.objects.get(user__id=user_id)
    if task == 'add':
        if request.method == 'POST':
            form = form(request.POST)
            client_id = request.POST.get('client')
            project_id = request.POST.get('project')
            available_task = request.POST.getlist('available_task')
            name = request.POST.get('name', '')
            if form.is_valid():
                f = form.save(commit=False)
                f.slug=name
                if client_id:
                    client_obj = Client.objects.get(pk=client_id)
                    f.client = client_obj
                #f.save()
                if project_id:
                    project_obj = Project.objects.get(pk=project_id)
                    f.project = project_obj
                f.save()
                if available_task:
                    for i in available_task:
                        f.available_task.remove(i)
                    for i in available_task:
                        f.available_task.add(i)
                        f.save()
                msg = "successfully saved"
                return HttpResponseRedirect("/milestones/")
            else:
                error = "form error"
                msg = "Please check the particulars"
    elif task == "edit":
        id_edit = id
        msg = ''
    #todays = datetime.date.today()+timedelta(days=7)
        mile = Milestone.objects.get(id=id_edit)
        f = Milestone_Form(request.user.pk)
        form = f(instance=mile)
        if request.POST:
            form = f(request.POST, instance=mile)
            available_task = request.POST.getlist('available_task', '')
            if form.is_valid():
                f = form.save(commit=False)
                #if not Milestone.objects.filter(title = request.POST.get\
                    #('title')).exclude(id=mile.id).exists():
                client_id = request.POST.get('client','')
                if client_id:
                    client_obj = Client.objects.get(pk=client_id)
                    f.client = client_obj
                project_id = request.POST.get('project','')
                if project_id:
                    project_obj = Project.objects.get(pk=project_id)
                    f.project = project_obj
                f.save()
                if available_task:
                    for i in available_task:
                        f.available_task.remove(i)
                    for i in available_task:
                        f.available_task.add(i)
                        f.save()
                    edit_done = True
                    msg = "edited successfully"
                    success = True
                return HttpResponseRedirect("/milestones/")
            else:
                 msg='Invalid form'
    return render(request, "milestones/milestone-add.html", locals(), 
                                    context_instance = RequestContext(request))

import datetime
@login_required(login_url="/login/")
def _filter_function(request, milestone_list):
    todays = datetime.date.today()
    #milestone_list = Milestone.objects.filter(owned_by__user=request.user)
    task = Tasks.objects.all()
    project_list=Project.objects.all()
    clients=Client.objects.all()
    peoples = UserProfile.objects.all()
    milestone = Milestone.objects.all()
    client_id = request.GET.get('client', '')
    project_id = request.GET.get('projects', '')
    owned_by_id = request.GET.get('owners', '')
    milestone_id = request.GET.get('milestones', '')
    title = request.GET.get('milestone-title', '')
    status = request.GET.get('status', '')
    if client_id:
        client_obj = Client.objects.filter(id=client_id)
        milestone_list = milestone_list.filter(client=client_obj)
    if project_id:
        milestone_list= milestone_list.filter(project__id=project_id)
    if owned_by_id:
        milestone_list = milestone_list.filter(owned_by__id=owned_by_id)
    if status:
        todays = datetime.date.today()
        if status == 'Overdue':
            milestone_list = milestone_list.filter(due_date__lt=todays, status=False)
        elif status == 'Complete':
            milestone_list = milestone_list.filter(status=True)
        elif status == 'In Progress':
            milestone_list = milestone_list.filter(status=False).exclude(due_date__lt=todays)
    if milestone_id:
        milestone_list = milestone_list.filter(milestone__id=milestone_id)
    if title:
        milestone_list = milestone_list.filter(title__icontains=title)
    milestoness=milestone_list
    return render(request, "milestones/milestone-home.html", locals())


import datetime
@login_required(login_url="/login/")
def mile(request):
    for i in request.user.userprofile_set.all():
        if i.access_level == '1':
            return _filter_function(request, Milestone.objects.all())
    return milestone_owned_by(request)


'''@login_required(login_url="/login/")
def editmilestone(request, id_edit):
    msg = ''
    #todays = datetime.date.today()+timedelta(days=7)
    mile = Milestone.objects.get(id=id_edit)
    form = MilestoneForm(instance = mile)
    if request.POST:
        form = MilestoneForm(request.POST, instance = mile)
        if form.is_valid():
            f = form.save(commit=False)
            if not Milestone.objects.filter(title = request.POST.get('title')).exclude(id=mile.id).exists():
                f.save()
                edit_done = True
                msg = "edited successfully"
                success = True
                return HttpResponseRedirect("/milestones/")
            else:
                msg = "Already Exists!!"
            print msg,'msg'
        else:
             msg='Invalid form'
    return render(request,"milestones/milestone-add.html",locals())
'''

import datetime
@login_required(login_url="/login/")
def milestone_owned_by(request):

    milestone_list = Milestone.objects.filter(owned_by__user=request.user)
    return _filter_function(request, milestone_list)


@login_required(login_url="/login/")
def milestone_documents(request):
    documents = Milestone_Document.objects.all()
    return render(request, "milestones/milestone-home.html", locals())


@login_required(login_url="/login/")
def addmilestonedocument(request):
    form = Milestone_DocumentForm()
    error = ''
    msg = ''
    nam = ''
    x = ''
    f = ''
    if request.method == 'POST':
        form = Milestone_DocumentForm(request.POST, request.FILES)
        files = request.POST.get('files')
        if form.is_valid():
            f = form.save(commit=False)
            f.save()
            msg = "successfully saved"
            return HttpResponseRedirect("/milestones/")
        else:
            error = "form error"
            msg = "invaid"
            
    return render(request, "milestones/milestonedocument.html", \
    locals(), context_instance = RequestContext(request))

@login_required(login_url="/login/")
def editmilestonedocument(request, id_edit):
    msg = ''
    doc = Milestone_Document.objects.get(id=id_edit)
    form = Milestone_DocumentForm(instance = doc)
    files = request.POST.get('files')
    if request.POST:
        form = Milestone_DocumentForm(request.POST, instance = doc)
        if form.is_valid():
            f = form.save(commit=False)
            if not Milestone_Document.objects.filter(files = request.POST.get('files')).exclude(id=doc.id).exists():
                f.save()
                edit_done = True
                msg = "edited successfully"
                success = True
                return HttpResponseRedirect("/milestones/")
            else:
                msg = "Already Exists!!"
        else:
             msg='Invalid form'
    return render(request, "milestones/milestonedocument.html", locals())


@login_required(login_url="/login/")
def activemilestones(request, id_active):
    milestone_obj = Milestone.objects.get(id=id_active)
    milestone_obj.activate = 2
    milestone_obj.save()
    success = True
    msg = "Milestone Deactivated Successfully"
    return HttpResponseRedirect("/milestones/")



@login_required(login_url="/login/")
def deletemilestones(request, id_delete):
    milestone_obj = Milestone.objects.get(id=id_delete)
    milestone_obj.activate = 0
    milestone_obj.save()
    success = True
    msg = "Milestone Deactivated Successfully"
    return HttpResponseRedirect("/milestones/")


import json
@login_required(login_url="/login/")
def gettasks(request):
    result={}
    cid = request.GET.get('cid')
    if cid:
        client_obj = Client.objects.get(id=cid)
        project_obj =Project.objects.filter(client=client_obj).values('id','name')
        result['res'] = list(project_obj)
    return HttpResponse(json.dumps(result),mimetype = "application/json")


@login_required(login_url = "/login/")
def gettasks_list(request):
    result = {}
    mid = request.GET.get('mid')
    if mid:
        tasks_obj = Tasks.objects.filter(project__id = mid).values('id','title')
        #Tasks.objects.filter(owned_by__user__id=id)
        result['res'] = list(tasks_obj)
    return HttpResponse(json.dumps(result), mimetype = "application/json")


import json
@login_required(login_url="/login/")
def getpeople(request):
    result={}
    pid = request.GET.get('pid')
    if pid:
        project_obj = Project.objects.get(id=pid)
        userprofile_obj =UserProfile.objects.filter(project=project_obj).values('id','first_name','last_name')
        result['res'] = list(userprofile_obj)
    return HttpResponse(json.dumps(result), mimetype = "application/json")


import json
@login_required(login_url="/login/")
def getstatus(request):
    result={}
    rid = request.GET.get('rid')
    if rid:
        employee_obj = Employee.objects.get(id=rid)
        milestone_obj = Milestone.objects.filter(employee=employee_obj).values('id','status')
        result['res'] = list(milestone_obj)
    return HttpResponse(json.dumps(result),mimetype = 'application/json')


import json
@login_required(login_url="/login/")
def getmilestones(request):
    result={}
    sid = request.GET.get('sid')
    if sid:
        milestone_obj =Milestone.objects.get(id=sid)
        milestones_obj =Milestone.objects.filter(milestone=milestone_obj).values('id','status')
        result['res'] = list(milestones_obj)
    return HttpResponse(json.dumps(result), mimetype = "application/json")



@login_required(login_url="/login/")
def import_data_m(request):
    key = request.GET.get('key')
    if request.method == "POST":
        csvfile = ''
        data_file = request.FILES.get('data_file')
        if key == "milestones":
            if data_file:
                csvfile = CSVFiles.objects.create(upload_file=data_file)
                csv_path = ('/home/mahadev/Desktop/pms/static/') + str(csvfile.upload_file)
                reader=csv.reader(open(csv_path,'rb'), delimiter=';')
                fields=reader.next()
                for i,item in enumerate(reader):
                    items = zip(fields,item)
                    row = {}
                    for (name,value) in items:
                        row[name]=value.strip()
                        pl = Project()
                    for x,y in row.items():
                       setattr(pl, x, y)
                    pl.save()
                msg_upload = "Uploaded Successfully.."
    return render(request, 'milestones/import-milestones.html', locals())



def search(request):
    try:
        q = request.GET['q']
        posts = Milestone.objects.filter(title__search=q)
        return render_to_response('milestones/index.html', locals())
    except KeyError:
        return render_to_response('milestones/index-home.html')


import datetime
@login_required(login_url="/login/")
def od(request):
    milestone_list = Milestone.objects.all()
    due_dates = milestone_list[0].due_date
    todays = datetime.date.today()
    return render(request,"milestones/od.html", locals(), context_instance = RequestContext(request))


def milestone_comment(request):
   success, msg, user, response = False, '', request.user, {}
   try:
       if request.method == 'POST':
           tid, val = request.POST.get('mid'), request.POST.get('val')
           if tid and val:
               milestone = Milestone.objects.get(pk = int(tid))
               content_type = ContentType.objects.get_for_model(milestone)
               site = Site.objects.get(pk = 1)
               comment = Comment.objects.create(content_type = content_type, \
               object_pk = milestone.pk, comment = val, user = user, site = site)
               success, msg = True, "Commented successfully."
           else:
               msg = "Invalid Data"
       else:
           msg = "Error Ocured"
   except Exception as e:
       msg = e.message
   response = {'success':success, 'msg':msg}
   return HttpResponse(json.dumps(response), mimetype="application/json")



