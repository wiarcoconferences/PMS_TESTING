from django.shortcuts import render
from people.models import *
from people.forms import *
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required
from projects.models import *
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
import csv
from django.contrib.contenttypes.models import ContentType
import datetime
from django.core.mail import send_mail
import uuid
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.contrib.auth.views import logout


from django.contrib.auth.models import Group, Permission
@login_required(login_url="/login/")
def person_list(request):
    user_profile = request.user.id
    project_obj = UserProfile.objects.get(user=user_profile)
    if project_obj.access_level == '1':
        projectobj = Project.objects.all()
        peoples_list = UserProfile.objects.all()
        client = Client.objects.all()
    else:
        projectobj = project_obj.project.all()
        peoples_list = [person
                        for project in projectobj
                            for person in project.get_peoples()]
        client = [projectobj.client for projectobj.client in projectobj]
    peoples = peoples_list
    if request.method == "POST":
        access_level = request.POST.get('access_level__id', '')
        if access_level:
            peoples_list = UserProfile.objects.filter(access_level=access_level)
        client_id = request.POST.get('client')
        if client_id:
            peoples_list = UserProfile.objects.filter(client=client_id)
        first_name = request.POST.get('person-name', '')
        if first_name:
            peoples_list =UserProfile.objects.filter(Q(first_name__icontains=first_name)| 
                                        Q(last_name__icontains=first_name))
        peoples = peoples_list
    return render(request, "people/persons-home.html", locals())


@login_required(login_url="/login/")
@permission_required('people.add_userprofile', login_url="/login/")
def people_details(request, task=None, id=''):
    msg = ''
    usr = ''
    clientobj = None
    resource_categorization_obj = None
    key = request.GET.get('key')
    form = UserForm()
    if task == "add":
        if request.method == 'GET' and not key == 'default':
            client_id = request.GET.get('client_id')
            clientobj = Client.objects.get(id = client_id)
        if request.method == 'GET' and key == 'default':
            form = UserForm()
        if request.method == "POST":
            form = UserForm(request.POST, request.FILES)
            profile_image = request.FILES.get('profile_image')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            title = request.POST.get('title')
            address = request.POST.get('address')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            access_level = request.POST.get('access_level', '')
            client = request.POST.get('client', '')
            name = request.POST.get('name', '')
            project_list = request.POST.getlist('project', '')
            resource_categorization = request.POST.get('resource_categorization', '')
            if form.is_valid():
#                check = UserProfile.objects.filter(first_name=first_name)
                if resource_categorization:
                    resource_categorization_obj = Resource_Categorization.objects.get(id=resource_categorization)
                if client:
                    try:
                        clientobj = Client.objects.get(id=client)
                #if password == retypepassword:
                    except:
                        pass
                    #except:
                        #pass
                #if not client:
                usr = User.objects.create_user(username=email, email=email, 
                first_name=first_name, last_name=last_name)
                u = uuid.uuid4()
                userprofile = UserProfile.objects.create(user=usr, first_name=first_name, 
                    last_name=last_name, title=title, address=address, email=email, 
                    phone=phone, profile_image=profile_image, access_level=access_level, 
                    client = clientobj,  uuid = u,
                    resource_categorization=resource_categorization_obj
                                            if resource_categorization_obj else None,)
                for a in project_list:
                    projectobj = Project.objects.get(id=int(a))
                    userprofile.project.add(projectobj)
                    userprofile.save()
                if userprofile.access_level is '2':
                    project_manager_obj , created = Project_Manager.objects.get_or_create(userprofile=userprofile)
                added = True
                success = True
                msg = "Successfully Registered."
                url = 'http://'+request.META['HTTP_HOST']+'/person/add-user/'+str(userprofile.uuid)+'/'
                body = "An Account has been created on PMS.\n\nPlease click on the below link to access your account : \n\n %s"%(url)
                print "----------->",request.user.email
                send_mail('Welcome To PMS', body, request.user.email, [userprofile.email,], fail_silently=False)
                return HttpResponseRedirect("/persons/")
                # else:
                #     msg = "Please fill the details"
            else:
                msg = "Name already exists"
    return render(request, "people/person.html", locals())


@login_required(login_url="/login/")
@permission_required('people.change_userprofile', login_url="/login/")
def useredit(request, task=None, id=None):
    msg = ""
    client_obj = None
    clientobj = None
    resource_categorization_obj= None
    if task == "edit":
        id_edit = id
        userobj = UserProfile.objects.get(id=id_edit)
        client_id = userobj.client
        form = UserEditForm(initial={'profile_image':userobj.profile_image, 
                'first_name': userobj.first_name, 'last_name': userobj.last_name, 
                'email': userobj.email, 'phone': userobj.phone, 
                'title':userobj.title, 'address': userobj.address, 
                 'access_level': userobj.access_level, 
                'client': userobj.client, 
                'project': userobj.project.all(), 
                'resource_categorization': userobj.resource_categorization})
        if request.method == "POST":
            form = UserEditForm(request.POST, request.FILES)
            if form.is_valid():
                profile_image = request.FILES.get('profile_image')
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                title = request.POST.get('title')
                address = request.POST.get('address')
                email = request.POST.get('email')
                phone = request.POST.get('phone')
                access_level = request.POST.get('access_level')
                client = request.POST.get('client')
                project_list = request.POST.getlist('project')
                resource_categorization = request.POST.get('resource_categorization', '')
                if client:
                    client_obj = Client.objects.get(id=int(client))
                else:
                    client_obj = None
                if resource_categorization:
                    resource_categorization_obj = Resource_Categorization.objects.get(id=int(resource_categorization))
                userobj.profile_image = profile_image
                userobj.first_name = first_name
                userobj.last_name = last_name
                userobj.title = title
                userobj.address = address
                userobj.email = email
                userobj.phone = phone
                userobj.access_level = access_level
                userobj.client = client_obj
                if project_list:
                    for a in project_list:
                        projectobj = Project.objects.get(id=int(a))
                        userobj.project.add(projectobj)
                        userobj.save()
                #else:
                 #   userobj.project = 'None'
                #else:
                 #   userobj.project = None
                userobj.resource_categorization = resource_categorization_obj if resource_categorization_obj else None
                userobj.save()
                
                if userobj.access_level == '2':
                    project_manager_obj = Project_Manager.objects.get_or_create(userprofile=userobj)
                edit_done = True
                success = True
                msg = 'Profile Edited Successfully'
                return HttpResponseRedirect("/persons/")
        else:
            msg =' Please Check all the fields are filled'
    elif task == "delete":
        id_delete = id
        userobj = UserProfile.objects.get(id=id_delete)
        userobj.active = 0
        userobj.save()
        success = True
        msg = "User Deactivated Successfully"
        response = {'msg': msg, 'success': success}
        return HttpResponseRedirect("/persons/")
    elif task == "active":
        id_active = id
        userobj = UserProfile.objects.get(id=id_active)
        userobj.active= 2
        userobj.save()
        success = True
        msg = "User Activated Successfully"
        response = {'msg':msg, 'success':success}
        return HttpResponseRedirect("/persons/")
    return render(request, "people/person.html", locals())


@login_required(login_url="/login/")
def display_people(request, id_disp):
    userprofile_obj = UserProfile.objects.get(id=id_disp)
    cont_type = ContentType.objects.get_for_model(userprofile_obj)
    news_feed = Recently_Viewed.objects.create(
        user=request.user, content_type=cont_type, object_id=userprofile_obj.id, )
    return render(request, "people/view-person.html", locals())

@login_required(login_url="/login/")
def assigning_projects_to_persons(request, id_assign):
    try:
        project_obj = Project.objects.get(id=int(id_assign))
        next = ('/project/view/' + str(project_obj.id) +'/')
        print next
    except:
        pass
    person_list = request.POST.getlist('person_list')
    if request.method == 'POST':
        try:
            
            userpro_obj = UserProfile.objects.all().exclude(pk__in = person_list)
            for j in userpro_obj:
                j.project.remove(project_obj)
                j.save()
            for i in person_list:
                userobj = UserProfile.objects.get(id=int(i))
                prj_ids = userobj.project.values_list('pk', flat = True)
                userobj.project.add(project_obj)
                userobj.save()
        except:
            pass
    return HttpResponseRedirect('/project/view/' + str(id_assign) +'/')


def login_user(request):
    msg = ''
    username = password = ''
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                msg = "welcome"
                userobj = request.user
                userprofile_obj = UserProfile.objects.get(email=userobj.email)
                if userprofile_obj.active == 2:
                    if userprofile_obj.access_level == '3':
                        if not userprofile_obj.project.all():
                            msg = "You dont have any project access. Please Contact Administrator"
                            return render(request, "people/login.html", locals())
                        else:
                            return HttpResponseRedirect('/home/')
                    else:
                        return HttpResponseRedirect('/home/')
                else:
                    msg = "Your account is not active please contact adminstrator"
            else:
                msg = 'your acc is not active'
        else:
             msg = 'Please Check Your Username and Password'
    return render(request, "people/login.html", locals())


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/login/')


#def change_password(request):
#    return render(request, '')


@login_required(login_url="/login/")
def import_data(request):
    key = request.GET.get('key')

    if request.method == "POST":
        csvfile = ''
        data_file = request.FILES.get('data_file')
        if key == "peoples":
            if data_file:
                csvfile = CSVFiles.objects.create(upload_file=data_file)
                csv_path = ('/home/raju/Desktop/pms/static/') + str(csvfile.upload_file)
                reader=csv.reader(open(csv_path, 'rb'), delimiter=';')
                fields=reader.next()
                for i, item in enumerate(reader):
                    items = zip(fields, item)
                    row = {}
                    for (name, value) in items:
                        row[name]=value.strip()
                        pl = Project()
                    for x, y in row.items():
                       setattr(pl, x, y)
                    pl.save()
                msg_upload = "Uploaded Successfully.."
    return render(request, 'people/import-people.html', locals())


@login_required(login_url="/login/")
def import_data(request):
    key = request.GET.get('key')

    if request.method == "POST":
        csvfile = ''
        data_file = request.FILES.get('data_file')
        if key == "peoples":
            if data_file:
                csvfile = CSVFiles.objects.create(upload_file=data_file)
                csv_path = ('/home/raju/Desktop/pms/static/') + str(csvfile.upload_file)
                reader=csv.reader(open(csv_path, 'rb'), delimiter=';')
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
    return render(request, 'people/import-people.html', locals())


#@login_required(login_url="/login/")
def person_add(request, unval=""):
    success, user, error = False, '', ''
    if unval == "":
        unval = request.GET.get('unval')
    if unval:
        try:
            user_profile = UserProfile.objects.get(uuid=unval)
        except:
            success = False
        if request.method == 'POST':
            username = request.POST.get('username')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if username and password1 and password2:
                try:
                    user = User.objects.filter(username=username)
                except:
                    pass
                if not user:
                    if password1 == password2:
                        email = user_profile.user.email
                        user = User.objects.get(email=email)
                        user.username = username
                        user.set_password(password2)
                        user.save()
                        userprofile_obj = UserProfile.objects.get(user=user)
                        if userprofile_obj.access_level == '1':
                            user.groups.add(Group.objects.get(name__iexact="Administrator"))
                        if userprofile_obj.access_level == "2":
                            user.groups.add(Group.objects.get(name__iexact="Project Manager"))
                        if userprofile_obj.access_level == '3':
                            user.groups.add(Group.objects.get(name__iexact="Resource"))
                        return HttpResponseRedirect('/login/')
                    else:
                        error = "Passwords should be match."
                else:
                    error = "User already exist."
            else:
                error = "Invalid Data."
    return render(request, 'people/person_add.html', locals())









