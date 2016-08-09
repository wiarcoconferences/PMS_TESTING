from django.shortcuts import render
from documents.models import Document
from documents.forms import *
from django.contrib.contenttypes.models import ContentType
from documents.forms import TaskDocumentForm
from projects.models import Project
from projects.models import Project_Module_Relationship
from projects.models import Project_Manager
from people.models import UserProfile
from client.models import Client
from client.models import Base
from django.http import HttpResponseRedirect, HttpResponse, Http404
import json
from django.contrib.auth.decorators import login_required

@login_required(login_url="/login/")
def my_documents(request):
    user = request.user
    userprofile_obj = UserProfile.objects.get(user=user.id)
    if userprofile_obj.access_level == '1' :
        documents = Document.objects.all()
    else:
        documents = Document.objects.filter(person=userprofile_obj)
    return render(request, "documents/documents-home.html", locals())


@login_required(login_url="/login/")
def documents_home(request):
    user = request.user
    userprofile_obj = UserProfile.objects.get(user=user.id)
    if userprofile_obj.access_level == '1' :
        documents = Document.objects.all()
    else:
        documents = Document.objects.filter(person=userprofile_obj)
    projects = Project.objects.all()
    client = Client.objects.all()
    return render(request, "documents/documents-home.html", locals())

#def documents_list():
    #user = request.user
    #documents = Document.objects.filter(user=user)
    #return render(request, "documents/documents-home.html", locals())


@login_required(login_url="/login/")
def documents_details(request, task=None):
    """ Document Details Add """
    response = {}
    check = ''
    tasks_obj = None
    added = ''
    milestone_obj = None,
    
    msg = ''
    f = Document_Form(request.user.pk)
    form = f
    Success = False
#import ipdb;ipdb.set_trace();
    if task == 'add':
        if request.method == "POST":
            form = form(request.POST, request.FILES)
            person = request.POST.get('person')
            title = request.POST.get('title', '')
            tags = request.POST.get('tags', '')
            notes = request.POST.get('notes', '')
            files = request.FILES.get('files','')
            project = request.POST.get('project')
            milestone = request.POST.get('milestone', '')
            tasks = request.POST.get('tasks', '')
            if project:
                project_obj = Project.objects.get(id=project)
            if person:
                userprofile_obj = UserProfile.objects.get(id=person)
            if tasks:
                tasks_obj = Tasks.objects.get(id=tasks)
            if milestone:
                milestone_obj = Milestone.objects.get(id=milestone)
            document_obj = Document.objects.create(person=userprofile_obj, title=title, tags=tags, files=files, notes=notes, project=project_obj, tasks=tasks_obj if tasks else None, milestone=milestone_obj if milestone else None)
            document_obj.save()
            added = True
            return HttpResponseRedirect("/documents/documents-home/")
            #else:
                #msg = 'Form Error'

    if task == "edit":
        edit = True
        id_edit = request.GET.get('id')
        document_obj = Document.objects.get(id=id_edit)
        form = Document_Form(request.user.id)
        form = form(initial={'title': document_obj.title, 'tags': document_obj.tags, 'notes': document_obj.notes, 'files': document_obj.files, 'person': document_obj.person, 'project':document_obj.project, 'tasks':document_obj.tasks , 'milestone': document_obj.milestone})
        if request.method == "POST":
            form = Document_Form(request.user.pk,request.POST,request.FILES)
            person = request.POST.get('person')
            title = request.POST.get('title', '')
            project = request.POST.get('project')
            tasks = request.POST.get('tasks')
            milestone = request.POST.get('milestone')
            tags = request.POST.get('tags', '')
            notes = request.POST.get('notes', '')
            files = request.FILES.get('files')
            document_obj.title = title
            document_obj.tags = tags
            document_obj.notes = notes
            document_obj.notes = tasks
            if files:
                document_obj.files = files
            if project:
                project_obj = Project.objects.get(id=project)
            if person:
                userprofile_obj = UserProfile.objects.get(id=person)
            if tasks:
                tasks_obj = Tasks.objects.get(id=tasks)
            if milestone:
                milestone_obj = Milestone.objects.get(id=milestone)
            document_obj.tasks = tasks_obj
            document_obj.milestone = milestone_obj
            document_obj.person = userprofile_obj
            
            document_obj.save()
            return HttpResponseRedirect("/documents/documents-home/")
    if task == "active":
        id_active = request.GET.get('id')
        docs = Document.objects.get(id=id_active)
        docs.active = 2
        docs.save()
        msg = "Document activated successfully"
        return HttpResponseRedirect("/documents/documents-home/")
    if task == "delete":
        id_delete = request.GET.get('id')
        docs = Document.objects.get(id=id_delete)
        docs.active = 0
        docs.save()
        msg = 'Document Deleted Successfully'
        return HttpResponseRedirect("/documents/documents-home/")
    return render(request, "documents/documents.html", locals())


def get_milestone_tasks(request):
    results = {}
    if request.is_ajax():
        bid=request.GET.get("id")
        if bid:
            project_obj = Project.objects.get(id=bid)
            milestone_list = Milestone.objects.filter(project=project_obj).values('id', 'title')
            results['res'] = list(milestone_list)
            return HttpResponse(json.dumps(results), mimetype="application/json")
    return render(request, "documents/documents.html", locals())


def get_ajax_tasks(request):
    user = request.user.id
    person = UserProfile.objects.get(user=user)
    results = {}
    if request.is_ajax():
        bid=request.GET.get("id")
        if bid:
            project_obj = Project.objects.get(id=bid)
            task_list = Tasks.objects.filter(project=project_obj, owned_by__id=person.id).values('id', 'title')
            results['res'] = list(task_list)
            return HttpResponse(json.dumps(results), mimetype="application/json")
    return render(request, "documents/documents.html", locals())


def add_document(request, tid=''):
    if tid=='':
        tid = request.GET.get('tid')
    form = TaskDocumentForm()
    if request.method == "POST":
        form = TaskDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.content_type = ContentType.objects.get(name__iexact='tasks')
            obj.objects_id = tid
            obj.save()
            return HttpResponseRedirect('/tasks/view/'+tid+'/')
        else:
            form = TaskDocumentForm(request.POST, request.FILES)
            error = "Invalid Form"
    return render(request, "documents/add-document.html", locals())


def edit_document(request, tid=''):
    edit = True
    if tid =='':
        tid = request.GET.get('tid')
    document = Document.objects.get(id=tid)
    form = TaskDocumentForm(instance=document)
    if request.method == 'POST':
        form = TaskDocumentForm(request.POST, request.FILES, instance=document )
        if form.is_valid():
            if request.POST.get('title') == document.title or \
                not Document.objects.filter(title__iexact=request.POST.get('title')).exclude(id=tid).exists():
                form.save()
                return HttpResponseRedirect('/tasks/')
            else:
                error = "Document With this title already exists"
        else:
            msg = "Invalid Form"
    return render(request, "documents/add-document.html", locals())


def delete_document(request,tid=''):
    if tid == '':
        tid = request.GET.get('tid')
    task_id = request.GET.get('task_id')
    document = Document.objects.get(id=tid)
    document.active = False
    document.save()
    return HttpResponseRedirect('/tasks/view/'+task_id+'/')


def activate_document(request, tid=''):
    if tid == '':
        tid = request.GET.get('tid')
    task_id = request.GET.get('task_id')
    document = Document.objects.get(id=tid)
    document.active=True
    document.save()
    return HttpResponseRedirect('/tasks/view/'+task_id+'/')


def tags_list(request):
    userobj = UserProfile.objects.get(email=request.user.email)
    obj = Document.objects.filter(tags__icontains=userobj.first_name)
    return render(request, "documents/documents-tags.html", locals())













