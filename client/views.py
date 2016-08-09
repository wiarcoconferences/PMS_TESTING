from django.shortcuts import render
from client.models import Client
from client.forms import ClientForm
from django.http import HttpResponseRedirect, HttpResponse, Http404
from projects.forms import *
from projects.models import Project_Manager
from projects.models import Project
from tasks.models import *
from pms.settings import *
from django.contrib.auth.decorators import login_required
import json
from datetime import *
import csv
from django.contrib.auth.decorators import permission_required
import datetime


@login_required(login_url="/login/")
def home(request):
    tasks_status = Task_Statuses.objects.all()
    task_priorities = Task_priorities.objects.all()
    userprofile_list = UserProfile.objects.all()

    logged_in = request.user.userprofile_set.all()
    if '1' in (i.access_level for i in logged_in):
        clients = Client.objects.all()
        projects = Project.objects.all()
        milestones = Milestone.objects.all()
        modules = Modules.objects.all()
    else:
        projects = [project
                    for profile in logged_in
                    for project in profile.project.all()]
        clients = [project.client for project in projects]
        milestones = [milestone
                      for project in projects
                      for milestone in project.milestone_set.all()]
        modules = Modules.objects.all()
    delta = datetime.timedelta
    today_date = date.today()
    date_t = datetime.date.today()
    start_week = date_t - delta(date_t.weekday())
    end_week = start_week + delta(7)

    tasks_list = Tasks.objects.filter(owned_by__user=request.user)
    tasks_list = tasks_list.filter(start_date__range=[start_week, end_week])

    clients_id = request.POST.get('client')
    if clients_id:
        clients_obj = Client.objects.get(id=clients_id)
        tasks_list = tasks_list.filter(project__client=clients_obj)

    projects_id = request.POST.get('project')
    if projects_id:
        projects_obj = Project.objects.get(id=projects_id)
        tasks_list = tasks_list.filter(project=projects_obj)

    milestones_id = request.POST.get('milestone')
    if milestones_id:
        milestone_obj = Milestone.objects.get(id=milestones_id)
        tasks_list = tasks_list.filter(milestone=milestone_obj)

    modules_id = request.POST.get('modules')
    if modules_id:
        modules_obj = Modules.objects.get(id=modules_id)
        tasks_list = tasks_list.filter(module=modules_obj)

    tasks_status_id = request.POST.get('tasks_status')
    if tasks_status_id:
        tasks_status_obj = Task_Statuses.objects.get(id=tasks_status_id)
        tasks_list = tasks_list.filter(status=tasks_status_obj)

    task_priorities_id = request.POST.get('task_priorities')
    if task_priorities_id:
        task_priorities_obj = Task_priorities.objects.get(id=task_priorities_id)
        tasks_list = tasks_list.filter(priority=task_priorities_obj)

    owner_id = request.POST.get('owner')
    if owner_id:
        owner_obj = UserProfile.objects.get(id=owner_id)
        tasks_list = tasks_list.filter(owned_by=owner_obj)

    assigned_id = request.POST.get('assigned')
    if assigned_id:
        assigned_obj = UserProfile.objects.get(id=assigned_id)
        tasks_list = tasks_list.filter(assigned_to=assigned_obj)

    follower_id = request.POST.get('follower')
    if follower_id:
        follower_obj = UserProfile.objects.get(id=follower_id)
        tasks_list = tasks_list.filter(followed_by=follower_obj)

    data = [(i,
             sum(float(task.actual)
                 for task in tasks_list.filter(
                         start_date=start_week+delta(i-1))))
            for i in range(1,8)]

    user_id = request.user.id
    overdue_milestones = Milestone.objects.filter\
                         (owned_by__user__id=user_id, due_date__lt=date_t, status=False)
    task_list = Tasks.objects.filter(due_date__lt=date_t).exclude\
                (status=Task_Statuses.objects.get(name='Closed'))

    overdue_tasks = []
    for od_tasks in task_list:
        if od_tasks.owned_by.filter(user__id=user_id).exists():
            overdue_tasks.append(od_tasks)
        else:
            pass
    task_dd_list = Tasks.objects.filter(due_date=None)
    no_due_date_tasks = filter(lambda obj: obj.owned_by.filter(user__id=user_id).exists(), task_dd_list)

    return render(request, "home.html", locals())


@login_required(login_url="/login/")
@permission_required('client.add_client', login_url="/login/")
def client_list(request):
    result = {}
    client_list = Client.objects.all()
    projects = Project.objects.all()
    name = request.POST.get('client-name', '')
    client_list = Client.objects.filter(name__icontains=name)
    client = client_list
    return render(request, "client/clients-home.html", locals())


@login_required(login_url="/login/")
@permission_required('client.add_client', login_url="/login/")
def client_details(request, task=None, id=None):
    """ Client Details Add """
    response = {}
    check = ''
    msg = ''
    Success = False
    if task == 'add':
        id = None
        form = ClientForm()
        if request.method == "POST":
            form = ClientForm(request.POST)
            name = request.POST.get('name', '')
            description = request.POST.get('description', '')
            address = request.POST.get('address', '')
            email = request.POST.get('email', '')
            phone = request.POST.get('phone', '')
            website = request.POST.get('website', '')
            fax = request.POST.get('fax', '')
            if form.is_valid():
                check = Client.objects.filter(email=email)
                check1 = Client.objects.filter(name=name)
                print "email", email
                if not check:
                    if not check1:
                        client_obj = Client.objects.create(
                            name=name, description=description, address=address, email=email, phone=phone, website=website, fax=fax)
                        added = True
                        success = True
                        return HttpResponseRedirect("/clients/")
                    else:
                        msg = " Name already Exists "
                else:
                    msg = "Email Already Exists"
            else:
                msg = "Error Occured"
    elif task == "edit":
        id_edit = id
        clientobj = Client.objects.get(id=id_edit)
        form = ClientForm(initial={'name': clientobj.name,
                                   'description': clientobj.description, 'address': clientobj.address,
                                   'email': clientobj.email, 'phone': clientobj.phone,
                                   'website': clientobj.website, 'fax': clientobj.fax})
        if request.method == 'POST':
            form = ClientForm(request.POST)
            if form.is_valid():
                name = request.POST.get('name', '')
                description = request.POST.get('description', '')
                address = request.POST.get('address', '')
                email = request.POST.get('email', '')
                phone = request.POST.get('phone', '')
                website = request.POST.get('website', '')
                fax = request.POST.get('fax', '')
                clientobj.name = name
                clientobj.description = description
                clientobj.address = address
                clientobj.email = email
                clientobj.phone = phone
                clientobj.website = website
                clientobj.fax = fax
                clientobj.save()
                edit_done = True
                success = True
                msg = 'Client Edited Successfully'
                return HttpResponseRedirect("/clients/")
            else:
                msg = 'Invalid Data'
#           response = {'msg':msg, 'success':success}
    elif task == "delete":
        id_delete = id
        clientobj = Client.objects.get(id=id_delete)
        clientobj.status = 1
        clientobj.save()
        success = True
        msg = "Client Deactivated Successfully"
        return HttpResponseRedirect("/clients/")
    elif task == "active":
        active = id
        clientobj = Client.objects.get(id=active)
        clientobj.status = 2
        clientobj.save()
        success = True
        msg = "Client Activated Successfully"
        return HttpResponseRedirect("/clients/")
    return render(request, "client/client.html", locals())


@login_required(login_url="/login/")
@permission_required('client.can_view_client', login_url="/login/")
def display_client(request, id_disp):
    client = Client.objects.all()

    client_obj = Client.objects.get(id=int(id_disp))
    cont_type = ContentType.objects.get_for_model(client_obj)
    news_feed = Recently_Viewed.objects.create(
        user=request.user, content_type=cont_type, object_id=client_obj.id, )
    return render(request, "client/client-view.html", locals())


@login_required(login_url="/login/")
@permission_required('client.can_view_client', login_url="/login/")
def dash_client(request, id_disp):
    client = Client.objects.all()
    client_obj = Client.objects.get(id=int(id_disp))
    project_list = client_obj.get_projects()
    proj_obj = Project.objects.all()
    return render(request, "client/client-dashboard.html", locals())


@login_required(login_url="/login/")
def deactivate_client(request):
    id_delete = request.GET.get('id')
    clientobj = Client.objects.get(id=id_delete)
    clientobj.status = 0
    clientobj.save()
    msg = "Client Deactivated Successfully"
    return HttpResponseRedirect("/client/view/")


@login_required(login_url="/login/")
def client_edit(request):
    id_edit = request.GET.get('id')
    clientobj = Client.objects.get(id=id_edit)
    form = ClientForm(initial={'name': clientobj.name,
                               'description': clientobj.description, 'address': clientobj.address,
                               'email': clientobj.email, 'phone': clientobj.phone, 'website': clientobj.website, 'fax': clientobj.fax})
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            name = request.POST.get('name', '')
            description = request.POST.get('description', '')
            address = request.POST.get('address', '')
            email = request.POST.get('email', '')
            phone = request.POST.get('phone', '')
            website = request.POST.get('website', '')
            fax = request.POST.get('fax', '')
            clientobj.name = name
            clientobj.description = description
            clientobj.address = address
            clientobj.email = email
            clientobj.phone = phone
            clientobj.website = website
            clientobj.fax = fax
            clientobj.save()
            edit_done = True
            success = True
            msg = 'Client Edited Successfully'
            return HttpResponseRedirect("/clients/")
            return render(request, "client/client.html", locals())


@login_required(login_url="/login/")
@permission_required('client.add_client', login_url="/login/")
def import_data(request):
    msg = ''
    key = request.GET.get('key')
    if request.method == "POST":
        csvfile = ''
        data_file = request.FILES.get('data_file')
        if key == "client":
            if data_file:
                csvfile = CSVFiles.objects.create(upload_file=data_file)
#                csv_path = ('/home/raju/Desktop/pms/static/') + str(csvfile.upload_file)
                csv_path = STATICFILES_DIRS[0] + "/" + str(csvfile.upload_file)
                reader = csv.reader(open(csv_path, 'rb'), delimiter=';')
                fields = reader.next()
                for i, item in enumerate(reader):
                    items = zip(fields, item)
                    row = {}
                    for (name, value) in items:
                        row[name] = value.strip()
                        pl = Client()
                    for x, y in row.items():
                        setattr(pl, x, y)
                    pl.save()
                    msg = "Uploaded Successfully.."
                return HttpResponseRedirect("/clients/")
        if key == "project":
            if data_file:
                csvfile = CSVFiles.objects.create(upload_file=data_file)
                csv_path = STATICFILES_DIRS[0] + "/" + str(csvfile.upload_file)
                reader = csv.reader(open(csv_path, 'rb'), delimiter=';')
                fields = reader.next()
                for i, item in enumerate(reader):
                    items = zip(fields, item)
                    row = {}
                    for (name, value) in items:
                        row[name] = value.strip()
                        pl = Project()
                    for x, y in row.items():
                        setattr(pl, x, y)
                    pl.save()
                    pl = Project()
    return render(request, "projects/import-project.html")


@login_required(login_url="/login/")
@permission_required('client.can_view_recently_viewed', login_url="/login/")
def recently_viewed(request):
    msg = ''
    key = request.GET.get('key')
    if key == 'client':
        recently_viewed = Recently_Viewed.objects.filter(
            user=request.user, content_type__model="client")[:5]
        return render(request, "client/recently_viewed.html", locals())
    if key == 'project':
        recently_viewed = Recently_Viewed.objects.filter(
            user=request.user, content_type__model="project")[:5]
        return render(request, "projects/recently_viewed.html", locals())
    if key == 'person':
        recently_viewed = Recently_Viewed.objects.filter(
            user=request.user, content_type__model="userprofile")[:5]
        return render(request, "people/recently_viewed.html", locals())
    if key == 'milestone':
        recently_viewed = Recently_Viewed.objects.filter(
            user=request.user, content_type__model="milestone")[:5]
        print recently_viewed
        return render(request, "milestones/recently_viewed.html", locals())
    if key == "task":
        recently_viewed = Recently_Viewed.objects.filter(
            user=request.user, content_type__model="tasks")[:5]
        return render(request, "tasks/recently_viewed.html", locals())
    if key == 'documents':
        recently_viewed = Recently_Viewed.objects.filter(
            user=request.user, content_type__model="document")[:5]
        return render(request, "documents/recently_viewed.html", locals())
