from django.shortcuts import render
from django.shortcuts import render, render_to_response
from django.core.paginator  import Paginator,InvalidPage, EmptyPage
from django.http import HttpResponse,HttpResponseRedirect
from tasks.models import Tasks
from tasks import *
from forms import *
from django.core.context_processors import csrf
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.template.defaultfilters import slugify
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import AnonymousUser
import csv
from people.models import UserProfile
from mastermodule.models import *
import datetime
from django.contrib.auth.decorators import login_required
import datetime
from django.contrib.comments import Comment
from django.contrib.sites.models import Site
from documents.models import *
from datetime import *


@login_required(login_url="/login/")
def task_add(request):
    key = ''
    try:
        mod = Modules.objects.get(name='Testing')
    except:
        pass
    key = 'add'
    form = TaskForm()
    error, msg, nam, x, f, mid = '', '', '', '', '', ''
    todays = datetime.date.today()
    todayss = datetime.date.today()+timedelta(days=7)
    messages = ''
    user_id = request.user.id
    user_id2 = UserProfile.objects.get(user__id=user_id)
    mid = request.GET.get('milestone_id')
    if mid:
        try:
            mobj = Milestone.objects.get(id=int(mid))
            proj_obj= mobj.project
            client_obj = mobj.client
        except:
            pass
    if request.method == 'POST':
        form = TaskForm(request.POST,request.FILES)
        name = request.POST.get('name', '')
        followed_by = request.POST.getlist('followed_by', '')
        assigned_to = request.POST.getlist('assigned_to', '')
        owned_by = request.POST.getlist('owned_by', '')
        if form.is_valid():
            f = form.save(commit=False)
            f.slug = name
            f.save()
            if followed_by:
                for i in followed_by:
                    f.followed_by.add(i)
                f.save()
            if assigned_to:
                for a in assigned_to:
                    f.assigned_to.add(a)
                f.save()
            if owned_by:
                for o in owned_by:
                    f.owned_by.add(o)
                f.save()
            #send_mail('A new Task has been added', 'Task has been created','spbraju@gmail.com',[userprofile.email], fail_silently=False)
            #print send_mail
            msg = "successfully saved"
            return HttpResponseRedirect("/tasks/")
        else:
            error = "form error"
    return render(request,"tasks/add-task.html", locals(), context_instance = RequestContext(request))


@login_required(login_url="/login/")
def add_multiple_tasks(request):
    form = TaskForm(prefix="task")
    subform = TaskForm(prefix="tas")
    subbform = TaskForm(prefix="tasks")
    error = ''
    msg = ''
    nam = ''
    x = ''
    f = ''
    s = ''
    ss = ''
    messages = ''
    if request.method == 'POST':
        form = TaskForm(request.POST or None, request.FILES, prefix="task")
        subform = TaskForm(request.POST or None, request.FILES, prefix="tas")
        subbform = TaskForm(request.POST or None,request.FILES , prefix="tasks")
        form_followed_by = request.POST.getlist('task-followed_by', '')
        form_assigned_to = request.POST.getlist('task-assigned_to', '')
        form_owned_by = request.POST.getlist('task-owned_by', '')
        subform_followed_by = request.POST.getlist('tas-followed_by', '')
        subform_assigned_to = request.POST.getlist('tas-assigned_to', '')
        subform_owned_by = request.POST.getlist('tas-owned_by', '')
        subbform_followed_by = request.POST.getlist('tasks-followed_by', '')
        subbform_owned_by = request.POST.getlist('tasks-owned_by', '')
        subbform_assingned_to = request.POST.getlist('tasks-assigned_to', '')
        if form.is_valid() and subform.is_valid() and subbform.is_valid():
            f = form.save(commit=False)
            f.slug = slugify(request.POST.get('task-name'))
            f.save()
            for i in form_followed_by:
                f.followed_by.add(i)
            #f.save()
            for a in form_assigned_to:
                f.assigned_to.add(a)
            #f.save()
            for o in form_owned_by:
                f.owned_by.add(o)
            f.save()
            s = subform.save(commit=False)
            s.slug=slugify(request.POST.get('tas-name'))
            s.save()
            for i1 in subform_followed_by:
                s.followed_by.add(i1)
            #s.save()
            for a1 in subform_assigned_to:
                s.assigned_to.add(a1)
            #s.save()
            for o1 in subform_owned_by:
                s.owned_by.add(o1)
            s.save()
            ss = subbform.save(commit=False)
            ss.slug = slugify(request.POST.get('tasks-name'))
            ss.save()
            for i2 in subbform_followed_by:
                ss.followed_by.add(i2)
            #ss.save()
            for a2 in subbform_assingned_to:
                ss.assigned_to.add(a2)
            #ss.save()
            for o2 in subbform_owned_by:
                ss.owned_by.add(o2)
            ss.save()
            msg = "successfully saved"
            return HttpResponseRedirect("/tasks/")
        else:
            error = "form error"
    return render(request, "tasks/add-multiple-task.html", locals(), context_instance = RequestContext(request))


@login_required(login_url="/login/")
def task_home(request):
    if  UserProfile.objects.filter(access_level=1):
        task_list = Tasks.objects.all()
    else:
        task_list = Tasks.objects.filter(owned_by__user=request.user)
    task_superset = Tasks.objects.filter(owned_by__user=request.user)
    modules = Modules.objects.all()
    status = Task_Statuses.objects.all()
    project = Project.objects.all()
    modules = Modules.objects.all()
    status = Task_Statuses.objects.all()
    priority = Task_priorities.objects.all()
    milestone = Milestone.objects.all()
    client = Client.objects.all()
    clients_list = Client.objects.all()
    client_id = request.GET.get('client', '')
    project_id = request.GET.get('projects', '')
    milestone_id = request.GET.get('milestones', '')
    module_id = request.GET.get('modules', '')
    priority_id = request.GET.get('priorities', '')
    status_id = request.GET.get('status', '')
    owned_by_id = request.GET.get('owners', '')
    followed_by_id = request.GET.get('followers', '')
    title = request.GET.get('task-title', '')
    if client_id:
        client_obj = Client.objects.filter(id=client_id)
        task_list = task_list.filter(client=client_obj)
    if project_id:
        task_list = task_list.filter(project__id=project_id)
    if module_id:
        task_list = task_list.filter(module__id=module_id)
    if status_id:
        task_list = task_list.filter(status__id=int(status_id))
    if priority_id:
        task_list = task_list.filter(priority__id=int(priority_id))
    if owned_by_id:
        task_list = task_list.filter(owned_by__id=owned_by_id)
    if milestone_id:
        task_list = task_list.filter(milestone__id=milestone_id)
    if title:
        task_list = task_list.filter(title__icontains=title)

    task = task_list
    todays = datetime.date.today()
    return render(request, "tasks/tasks-home.html", locals())


@login_required(login_url="/login/")
def task_edit(request, id_edit):
    msg = ''
    key = 'edit'
    task = Tasks.objects.get(id=id_edit)
    form = TaskForm(instance = task)
    user_id=request.user.id
    user_id2 = UserProfile.objects.get(user__id=user_id)
    if request.POST:
        form = TaskForm(request.POST, request.FILES, instance = task)
        if form.is_valid():
            #if not Tasks.objects.filter(title = request.POST.get('title')).exclude(id=task.id).exists():
            f = form.save(commit=False)
            f.save()
            foll_by_list = request.POST.getlist('followed_by')
            assig_to_list = request.POST.getlist('assigned_to')
            owned_by_list = request.POST.getlist('owned_by')
            for i in f.owned_by.all():
                f.owned_by.remove(i)
            for i in f.followed_by.all():
                f.followed_by.remove(i)
            for i in f.assigned_to.all():
                f.assigned_to.remove(i)
            for i in foll_by_list:
                f.followed_by.add(i)
            for i in assig_to_list:
                f.assigned_to.add(i)
            for i in owned_by_list:
                f.owned_by.add(i)
            f.save()
            #owned_list = request.POST.getlist('owned_by')
            #f.owned_by=owned_list
            #f.save()
            edit_done = True
            msg = "edited successfully"
            success = True
            return HttpResponseRedirect("/tasks/")
        else:
             msg='Invalid form'
    return render(request, "tasks/add-task.html", locals())


@login_required(login_url="/login/")
def add_task_request_to_new_task(request, id_disp):
    f = ''
    requestobj = Request.objects.get(id=int(id_disp))
    user_id = request.user.id
    user_id2 = UserProfile.objects.get(user__id=user_id)
    form = TaskForm()
    key = "request"
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            f = form.save(commit=False)
            f.save()
            return HttpResponseRedirect("/tasks/")
    return render(request, "tasks/add-task.html", locals())


@login_required(login_url="/login/")
def task_detail_view(request,id_disp):
    ta = Tasks.objects.get(id=id_disp)
    content_type = ContentType.objects.get_for_model(ta)
    comment = Comment.objects.filter(content_type = content_type, object_pk = ta.pk, is_public = True)
    doc = Document.objects.filter(content_type = content_type, objects_id = ta.pk )
    todays = datetime.date.today()
    cont_type = ContentType.objects.get_for_model(ta)
    news_feed = Recently_Viewed.objects.create(user = request.user, content_type = cont_type, object_id = ta.id,)
    return render(request, "tasks/task_view.html", locals())


import datetime
@login_required(login_url="/login/")
def task_overdue(request):
    todays = datetime.date.today()
    id_open = Task_Statuses.objects.get(name='Closed')
    overdue_list = Tasks.objects.filter(due_date__lt=todays).exclude(status__name='Closed')
    overdue_list = overdue_list
    return render(request, "tasks/task_overdue.html", locals())


@login_required(login_url="/login/")
def task_assigned(request):
    #user=request.user.email
    user_list = UserProfile.objects.filter(email=request.user.email)
    uid_list = []
    for i in user_list:
        uid_list.append(i.id)
    task__list = Tasks.objects.filter(assigned_to__in=list(set(uid_list)))
    task_list = Tasks.objects.filter(owned_by__user=request.user)
    modules = Modules.objects.all()
    status = Task_Statuses.objects.all()
    project = Project.objects.all()
    modules = Modules.objects.all()
    status = Task_Statuses.objects.all()
    priority = Task_priorities.objects.all()
    milestone = Milestone.objects.all()
    client = Client.objects.all()
    clients_list = Client.objects.all()
    client_id = request.GET.get('client', '')
    project_id = request.GET.get('projects', '')
    milestone_id = request.GET.get('milestones', '')
    module_id = request.GET.get('modules', '')
    priority_id = request.GET.get('priorities', '')
    status_id = request.GET.get('status', '')
    owned_by_id = request.GET.get('owners', '')
    followed_by_id = request.GET.get('followers', '')
    title = request.GET.get('task-title', '')
    if client_id:
        client_obj = Client.objects.filter(id=client_id)
        task_list = task_list.filter(client=client_obj)
    if project_id:
        task_list = task_list.filter(project__id=project_id)
    
    if module_id:
        task_list = task_list.filter(module__id=module_id)
    if status_id:
        task_list = task_list.filter(status__id=int(status_id))
    if priority_id:
        task_list = task_list.filter(priority__id=int(priority_id))
    if owned_by_id:
        task_list = task_list.filter(owned_by__id=owned_by_id)
    if milestone_id:
        task_list = task_list.filter(milestone__id=milestone_id)
    if title:
        task_list = task_list.filter(title__icontains=title)
    
    task = task_list
    return render(request, "tasks/assigned-to.html", locals())


@login_required(login_url="/login/")
def task_ownedby(request):
    user_list = UserProfile.objects.get(email=request.user.email)
    task_ownedby_list = Tasks.objects.filter(owned_by=user_list)
    return render(request, "tasks/ownedby.html", locals())


@login_required(login_url="/login/")
def task_following(request):
    clients = Client.objects.all()
    modules = Modules.objects.all()
    task_list = Tasks.objects.all()
    user_list = UserProfile.objects.filter(email=request.user.email)
    uid_list = []
    for i in user_list:
        uid_list.append(i.id)
    task_following_list = Tasks.objects.filter(followed_by__in=list(set(uid_list)))
    return render(request, "tasks/task_following.html", locals())


def task_with_no_assignees(request):
    key = request.GET.get('key')
    if key == 'no_assignee':
        tasks_no_assignee = Tasks.objects.filter(assigned_to=None)
        return render(request, "tasks/tasks-with-no-assignee.html", locals())
    if key == 'unclosed':
        tasks_not_closed = Tasks.objects.filter(status__name='Open')
        return render(request, "tasks/tasks_not_closed.html", locals())


@login_required(login_url="/login/")
def deletetasks(request, id_delete):
    p = Tasks.objects.get(id=id_delete)
    p.delete()
    return HttpResponseRedirect("/tasks/")


@login_required(login_url="/login/")
def search(request):
    try:
        q = request.GET['q']
        posts = Tasks.objects.filter(title__search=q)
        return render(request, 'tasks/tasks-home.html', locals())
    except KeyError:
        return render(request, 'tasks/tasks-home.html')


@login_required(login_url="/login/")
def task_requests(request):
    requests = Request.objects.all()
    return render(request, "tasks/request.html", locals())


@login_required(login_url="/login/")
def task_request_view(request,id_disp):
    request_list = Request.objects.get(id=id_disp)
    return render(request, "tasks/request_view.html", locals())


import datetime
@login_required(login_url="/login/")
def task_request_add(request):
    form = RequestForm()
    error = ''
    msg = ''
    nam = ''
    x = ''
    f = ''
    todays = datetime.date.today()+timedelta(days=7)
    messages = ''
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES)
        doc = request.POST.get('name')
        if form.is_valid():
            f = form.save(commit=False)
            f.save()
            frm_id = request.POST.get('frm')
            frmobj = Request.objects.get(id=frm_id)
            email = frmobj.frm.email
            print "email=======",email
            #send_mail('sucbject','Welcome To PMS', 'spbraju@gmail.com',[email], fail_silently = False)
            msg = "successfully saved"
            #print "send_mail",send_mail
            return HttpResponseRedirect("/task/requests/")
        else:
            error = "form error"
    return render(request,"tasks/add-request.html", locals(), context_instance = RequestContext(request))

@login_required(login_url="/login/")
def doc(request):
    document = Document.objects.all()
    return render(request, "documents/tasks-home.html", locals())


@login_required(login_url="/login/")
def task_request_edit(request, id_edit):
    msg = ''
    requests = Request.objects.get(id=id_edit)
    form = RequestForm(instance = requests)
    doc = request.POST.get('doc')
    if request.POST:
        form = RequestForm(request.POST,request.FILES, instance = requests)
        if form.is_valid():
            f = form.save(commit=False)
            f.save()
            edit_done = True
            msg = "edited successfully"
            success = True
            return HttpResponseRedirect("/task/requests/")
        else:
             msg='Invalid form'
    return render(request, "tasks/add_request.html", locals())


import json
@login_required(login_url="/login/")
def gettasks(request):
    result={}
    cid = request.GET.get('cid')
    if cid:
        client_obj = Client.objects.get(id=cid)
        project_obj =Project.objects.filter(client=client_obj).values\
        ('id', 'name')
        result['res'] = list(project_obj)
    return HttpResponse(json.dumps(result), mimetype = "application/json")


import json
@login_required(login_url="/login/")
def getmilestones(request):
    result={}
    pid = request.GET.get('pid')
    if pid:
        project_obj = Project.objects.get(id=pid)
        print project_obj,"project_obj"
        milestone_obj =Milestone.objects.filter(project=project_obj).values\
        ('id', 'title')
        result['res'] = list(milestone_obj)
    return HttpResponse(json.dumps(result),mimetype = "application/json")


import json
@login_required(login_url="/login/")
def getmodules(request):
    result={}
    pid = request.GET.get('pid')
    if pid:
        project_obj = Project.objects.get(id=pid)
        print project_obj
        module_obj = Project_Module_Relationship.objects.filter\
        (project=project_obj).values('id','project')
    return HttpResponse(json.dumps(result), mimetype="application/json")


@login_required(login_url="/login/")
def import_data(request):
    key = request.GET.get('key')
    if request.method == "POST":
        csvfile = ''
        data_file = request.FILES.get('data_file')
        if key == "tasks":
            if data_file:
                csvfile = CSVFiles.objects.create(upload_file=data_file)
                csv_path = ('/home/raju/Desktop/pms/static/') + str(csvfile.upload_file)
                reader=csv.reader(open(csv_path,'rb'), delimiter=';')
                fields=reader.next()
                for i,item in enumerate(reader):
                    items = zip(fields, item)
                    row = {}
                    for (name,value) in items:
                        row[name]=value.strip()
                        pl = Project()
                    for x,y in row.items():
                       setattr(pl, x, y)
                    pl.save()
                msg_upload = "Uploaded Successfully.."
    return render(request, 'tasks/import-tasks.html', locals())


@login_required(login_url="/login/")
def task_commend(request):
    success, msg, user, response = False, '', request.user, {}
    try:
        if request.method == 'POST':
            tid, val = request.POST.get('tid'), request.POST.get('val')
            if tid and val:
                task = Tasks.objects.get(pk = int(tid))
                content_type = ContentType.objects.get_for_model(task)
                site = Site.objects.get(pk = 1)
                comment = Comment.objects.create(content_type = content_type, object_pk = task.pk, comment = val, user = user, site = site)
                success, msg = True, "Commented successfully."
            else:
                msg = "Invalid Data"
        else:
            msg = "Error Ocured"
    except Exception as e:
        msg = e.message
    response = {'success':success, 'msg':msg}
    return HttpResponse(json.dumps(response), mimetype="application/json")


