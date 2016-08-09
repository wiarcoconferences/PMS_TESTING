from django.shortcuts import render
from projects.models import Project
from projects.models import Project_Manager
from projects.models import Project_Module_Relationship
from projects.forms import ProjectForm
from projects.forms import Project_ManagerForm
from client.models import Client
from django.http import HttpResponseRedirect, HttpResponse, Http404
from people.models import UserProfile
from client.models import Client
from mastermodule.models import *
from tasks.models import Tasks
import datetime
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.mail import send_mail
from client.models import Client

@login_required(login_url="/login/")
def project_list(request):
    userprofobj = UserProfile.objects.get(user = request.user)
    project_list = userprofobj.project.all()
    client = Client.objects.all()
    peoples = UserProfile.objects.filter(access_level='Manager')
    client_id = request.GET.get('client', '')
    project_id = request.GET.get('project', '')
    name = request.GET.get('project-name', '')
    clients_list = Client.objects.all()
    if client_id:
        client_obj = Client.objects.get(id=client_id)
        project_list = project_list.filter(client=client_obj)
    if project_id:
        project_list= project_list.filter(id=project_id)
    if name:
        project_list = project_list.filter(name__icontains=name)
    projects=project_list
    return render(request, "projects/projects-home.html", locals())
    
    
@login_required(login_url="/login/")
@permission_required('projects.add_project', login_url="/login/")
def project_profile(request, id_disp):
    proj_obj = Project.objects.get(id=id_disp)
    work_types = Work_Type.objects.all()
    modules = Modules.objects.all()
    get_users=proj_obj.get_user_profile()
    project_managers=proj_obj.get_managers()
    cont_type = ContentType.objects.get_for_model(proj_obj)
    recently_viewed = Recently_Viewed.objects.create(user=request.user, \
    content_type = cont_type,object_id=proj_obj.id)
    client = Client.objects.all()
    project_list = Project.objects.all()
    client_id = request.GET.get('client', '')
    project_id = request.GET.get('project', '')
    if client_id !=0 and project_id:
        client_obj = Client.objects.get(id=client_id)
        project_list = project_list.filter(client=client_obj)
        proj_obj = project_list[0]
    if project_id:
        project_list = project_list.filter(id=project_id)
        proj_obj = project_list[0]
    adminstrator = UserProfile.objects.filter(access_level='1')
    managers = UserProfile.objects.filter(access_level='2')
    resources = UserProfile.objects.filter(access_level='3')
    people = UserProfile.objects.all()

    return render(request,"projects/project-profile.html", locals())



import datetime
from datetime import timedelta
@login_required(login_url="/login/")
@permission_required('projects.add_project',login_url="/login/")
def project_details(request, task=None, id=None):
    response = {}
    msg = ''
    project_managerobj = ''
    Success = False
    today_date = datetime.date.today()
    due_date = datetime.date.today()+timedelta(7)
    form = ProjectForm()
    import ipdb; ipdb.set_trace();
    if task == 'add':
        if request.method == "GET":
            client = request.GET.get('client_id')
            if client:
                clientobj = Client.objects.get(id=int(client))
        if request.method == "POST":
            form = ProjectForm(request.POST)
            name = request.POST.get('name', '')
            description = request.POST.get('description', '')
            project_status = request.POST.get('project_status', '')
            start_date = request.POST.get('start_date', '')
            end_date = request.POST.get('end_date', '')
            budget = request.POST.get('budget', '')
            alert = request.POST.get('alert', '')
            client = request.POST.get('client', '')
            project_manager = request.POST.get('project_manager', '')
            if form.is_valid():
                if client:
                    clientobj = Client.objects.get(id = int(client))
                else:
                    clientobj = None
                check = Project.objects.filter(name=name)
                if check:
                    msg = "This Name already exists"
                if not check:
                    project_obj = Project.objects.create(name=name, 
                    description=description, project_status=project_status, 
                    alert=alert if alert else 0, 
                    start_date=start_date if start_date else None, 
                    end_date=end_date if end_date else None,
                    budget=budget if budget else 0)
                    if clientobj is not None:
                        project_obj.client = clientobj
                        project_obj.save()
                    if project_manager:
                        project_managerobj = Project_Manager.objects.get(id=int(project_manager))
                        project_obj.project_manager=project_managerobj
                        project_obj.save()
                        project_managerobj.userprofile.project.add(project_obj)
                        project_managerobj.save()
                    userprofile_obj = UserProfile.objects.filter(access_level='1')
                    if userprofile_obj:
#                        userprofileobj = [i.project for i.project.add(project_obj) ]
                        for i in userprofile_obj:
                            i.project.add(project_obj)
                            i.save()
                    default_module_list = Modules.objects.all()
                    if default_module_list:
                        for i in default_module_list:
                            cont_type = ContentType.objects.get_for_model(i)
                            object_id = i.id
                            Project_Module_Relationship.objects.create\
                            (project=project_obj, content_type=cont_type, object_id=object_id)
                    default_work_types_list=Work_Type.objects.all()
                    if default_work_types_list:
                        for i in default_work_types_list:
                            cont_type = ContentType.objects.get_for_model(i)
                            object_id = i.id
                            Project_Module_Relationship.objects.create\
                            (project=project_obj,content_type=cont_type,object_id=object_id)
                    added = True
                    success = True
                    if project_managerobj:
                        email = project_managerobj.userprofile.email
                        url = 'http://pms.mahiti.org/project/view/'+str(project_obj.id)+'/'
                        body = "This is a notification to let you know that \
                                project has been updated: %s \n\n Please click on the \
                                below link to view project."%(url)
                        send_mail('Project Manager Changed', body, 
                            request.user.email, [email,],fail_silently=False)
                    return HttpResponseRedirect("/projects/")
                #else:
                    #msg = "Name Already Exists"
            else:
                msg = " Something is a miss "
    
    elif task == "edit":
        id_edit = id
        project_obj = Project.objects.get(id=id_edit)
        if project_obj.client:
            clientobj = Client.objects.get(id=project_obj.client.id)
        form = ProjectForm(initial={
            'name':project_obj.name, 
            'description':project_obj.description,
            'project_status':project_obj.project_status, 
            'alert':project_obj.alert if project_obj.alert else None, 
            'start_date':project_obj.start_date, 
            'end_date':project_obj.end_date, 
            'budget':project_obj.budget if project_obj.budget else None, 
            'client':clientobj.id if project_obj.client else None, 
            'project_manager':project_obj.project_manager.id if
                              project_obj.project_manager else None})
        if request.method == "POST":
            form = ProjectForm(request.POST)
            if form.is_valid():
                name = request.POST.get('name', '')
                description = request.POST.get('description', '')
                project_status = request.POST.get('project_status', '')
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')
                budget = request. POST.get('budget', '')
                alert = request.POST.get('alert', '')
                client = request.POST.get('client')
                project_manager = request.POST.get('project_manager', '')
                project_obj.name = name
                project_obj.description = description
                project_obj.project_status = project_status
                project_obj.start_date = start_date if start_date else None 
                project_obj.end_date = end_date if end_date else None
                if budget:
                    project_obj.budget = budget 
                if alert:
                    project_obj.alert = alert 
                try:
                    project_obj.client = Client.objects.get(id=int(client))
                except:
                    project_obj.client = None
                try:
                    project_managerobj = Project_Manager.objects.get(id=int(project_manager))
                    #project_managerobj = Project_Manager.objects.get(id=int(project_manager))
                    project_managerobj.userprofile.project.add(project_obj)
                    project_managerobj.save()
                except:
                    project_managerobj = None
                if project_manager:
                    email = project_managerobj.userprofile.email
                    url = 'http://pms.mahiti.org/project/view/'+str(project_obj.id)+'/'
                    body = "This is a notification to let you know that project  has been updated: %s \n\n Please click on the below link to view project."%(url)
                    send_mail('Project Manager Changed', body, 
                                'spbraju@gmail.com', [email,],fail_silently=False)
                edit_done = True
                success = True
                project_obj.save()
                return HttpResponseRedirect("/projects/")
                msg = 'Project Edited Successfully'
    elif task == "delete":
        id_delete = id 
        project_obj = Project.objects.get(id=id_delete)
        project_obj.active = 1
        project_obj.save()
        success = True
        return HttpResponseRedirect("/projects/")
    elif task == "active":
        id_active = id 
        project_obj = Project.objects.get(id=id_active)
        project_obj.active = 2
        project_obj.save()
        success = True
        return HttpResponseRedirect("/projects/")
    return render(request, "projects/project.html", locals())


@login_required(login_url="/login/")
@permission_required('projects.can_view_project_manager', login_url="/login/")
def managers_details(request):
    project_managers = Project_Manager.objects.all()
    return render(request, "projects/managers.html", locals()) 


@login_required(login_url="/login/")
def project_dashboard(request, id_disp):
    project = Project.objects.all()
    a = Project.objects.get(id=id_disp)
    project_obj = a.get_unclosed_task_list.im_self.id
    projectobj = a.get_no_assignee_task_list.im_self.id
    return render(request, "projects/project-dashboard.html", locals())


@login_required(login_url="/login/")
def project_manager(request, task=None):
    response = {}
    msg = ''
    Success = False
    if task == 'add':
        form = Project_ManagerForm()
        if request.method == "POST":
            form = Project_ManagerForm(request.POST)
            project_manager = request.POST.get('Project_Manager')
            if form.is_valid():
                f= form.save()
                f.save()
                msg = "Successfully Fully Saved"
                return HttpResponseRedirect('/managers/')
            else:
                msg = 'Name Already Exist'
    elif task == "edit":
        response = {}
        msg = ''
        id_edit = request.GET.get('id')
        project_managerobj = Project_Manager.objects.get(id=id_edit)
        form = Project_ManagerForm(instance = project_managerobj)
        if request.POST:
            form = Project_ManagerForm(request.POST, instance=project_managerobj)
            if form.is_valid():
                f = form.save(commit=False)
                if not Project_Manager.objects.filter\
                (name = request.POST.get('nmae')).exclude(id=id_edit).exists():
                    f.save()
                    edit_done= True
                    msg = "Edited Successfully"
                    success = True
                    return HttpResponseRedirect("/managers/")
                else: 
                    msg = "Name Already Exist"
            else:
                msg = " "
    return render(request, "projects/manager.html", locals())
    
    
    
@login_required(login_url="/login/")
def import_data(request):
    msg = ''
    key = request.GET.get('key')
    if request.method == "POST":
        csvfile = ''
        data_file = request.FILES.get('data_file')
        if key == "project":
            if data_file:
                csvfile = CSVFiles.objects.get_or_create(upload_file=data_file)
                csv_path = STATICFILES_DIRS[0] + "/" +str(csvfile.upload_file)
                reader = csv.reader(open(csv_path, 'rb'), delimiter=';')
                fields=reader.next()
                for i,items in enumerate(reader):
                    items = zip(fields, item)
                    row = {}
                    for (name,value) in times:
                        row[name]=value.strip()
                        pl.project()
                    for x,y in row.items():
                        setattr(pl, x, y)
                    pl.save()
                
                    pl = Project()
    return render(request, "project/import-project.html" )


import json
def getprojects(request):
    user = request.user.id
    person = UserProfile.objects.get(user=user)
    project = person.project.all()
    #project_ids = [i.id for i in person.project.all()]
    result={}
    cid = request.GET.get('cid')
    if cid:
        client_obj = Client.objects.get(id=cid)
        project_obj =person.project.all().filter(client=client_obj).values('id', 'name')
        result['res'] = list(project_obj)
    return HttpResponse(json.dumps(result), mimetype="application/json")

def get_project_tasks(request):
    user = request.user.id
    person = UserProfile.objects.get(user=user)
    project_obj = person.project.all()
    result = {}
    
    pid = request.GET.get('pid')
    if pid:
        project_obj = Project.objects.get(id=pid)
        tasks_obj = Tasks.objects.filter(project=project_obj).values('id','title')
        result['res'] = list(tasks_obj)
    return HttpResponse(json.dumps(result), mimetype="application/json")


def getmodules(request):
    modules = Modules.objects.all()
    return render(request, "mastermodule/modules_home.html", locals())
    


def getclients(request):
    result ={}
    if pid:
        projects_obj = Project.objects.get(id=pid)
        clients_obj = project_obj.client
        result['res'] = list(clients_obj)
    return HttpResponse(json.dumps(result), mimetype="application/json")
    
    
