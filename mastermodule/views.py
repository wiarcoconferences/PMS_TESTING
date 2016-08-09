from django.shortcuts import render
from mastermodule.forms import *
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from mastermodule.models import Generalinfo
from tasks.models import Tasks
from people.models import UserProfile
from django.contrib.auth.decorators import login_required


#---------------------------------- Work_Type-------------------------------#

@login_required(login_url="/login/")
def budget(request, task=None):
    msg = ''
    Success = False

    if task == 'add':
        form = Work_TypeForm()
        if request.method == "POST":
            form = Work_TypeForm(request.POST)
            name = request.POST.get('name')
            hourly_rate = request.POST.get('hourly_rate')
            try:
                if hourly_rate:
                    hourly_rate = float(request.POST.get('hourly_rate'))
            except:
                msg = "Hour rate invalid"
                return render(request, "mastermodule/budget.html", locals())
            if form.is_valid():
                if Work_Type.objects.filter(name=name):
                    msg = "Name already exisits"
                else:
                    f = form.save(commit=False)
                    f.hourly_rate = hourly_rate
                    f.save()
                    added = True
                    success = True
                    return HttpResponseRedirect('/budgets/')

    elif task == "edit":
        response = {}
        msg = ''
        id_edit = request.GET.get('id')
        work_typeobj = Work_Type.objects.get(id=id_edit)
        hourly_rate = request.POST.get('hourly_rate')
        form = Work_TypeForm(instance=work_typeobj)
        if request.POST:
            form = Work_TypeForm(request.POST, instance=work_typeobj)
            try:
                if hourly_rate: hourly_rate = float(request.POST.get('hourly_rate'))
            except:
                msg = "Hour rate invalid"
                return render(request, "mastermodule/budget.html", locals())

            if form.is_valid():
                if Work_Type.objects.filter(name = request.POST.get('name')).exclude(id=id_edit).exists():
                    msg = "Name already exists"
                else:
                    f = form.save(commit=False)
                    f.save()
                    edit_done = True
                    msg = "Edited Successfully"
                    success = True
                    return HttpResponseRedirect("/budgets/")

    elif task == "delete":
        id_delete = request.GET.get('id')
        work_typeobj = Work_Type.objects.get(id=id_delete)
        work_typeobj.active = 0
        work_typeobj.save()
        success = True
        return HttpResponseRedirect("/budgets/")

    elif task == "active":
        id_active = request.GET.get('id')
        work_typeobj = Work_Type.objects.get(id=id_active)
        work_typeobj.active = 2
        work_typeobj.save()
        success = True
        return HttpResponseRedirect("/budgets/")
    return render(request, "mastermodule/budget.html", locals())


@login_required(login_url="/login/")
def budget_details(request):
    budgets = Work_Type.objects.all()
    return render(request, "mastermodule/budgets.html", locals())

#--------------------------------- Modules-----------------------------------#


@login_required(login_url="/login/")
def modules_details(request):
    mon = Modules.objects.all()
    return render(request, "mastermodule/modules-home.html", locals())



@login_required(login_url="/login/")
def modules(request,task=None):
    msg = ''
    response = ''
    msg = ''
    if task == "add":
        form = ModulesForm()
        if request.method == "POST":
            form = ModulesForm(request.POST)
            name = request.POST.get('name')
            description = request.POST.get('description')
            if form.is_valid():
                if Modules.objects.filter(name=name):
                    msg = 'Module already exist.'
                    return render(request, "mastermodule/modules.html", locals())
                else:
                    modules = Modules.objects.create(name=name, description=description)
                    added = True
                    success = True
                    return HttpResponseRedirect("/modules-home/")

    elif task == "edit":
        id_edit = request.GET.get('id')
        moduleobj = Modules.objects.get(id=id_edit)
        form = ModulesForm(initial={'name': moduleobj.name, 'description': moduleobj.description})
        if request.method == "POST":
            form = ModulesForm(request.POST)
            if form.is_valid():
                if Modules.objects.filter(name=request.POST.get('name')).exclude(id=moduleobj.id):
                    msg = 'Module already exist.'
                    return render(request, "mastermodule/modules.html", locals())
                else:
                    name = request.POST.get('name')
                    description = request.POST.get('description')
                    moduleobj.name = name
                    moduleobj.description = description
                    moduleobj.save()
                    added = True
                    success = True
                    msg = 'Module added Successfully'
                    return HttpResponseRedirect("/modules-home/")
        else:
                msg = ''
    elif task == "delete":
        id_delete = request.GET.get('id')
        moduleobj = Modules.objects.get(id=id_delete)
        moduleobj.active = 0
        moduleobj.save()
        success = True
        msg = "Module Deactivated Successfully"
        return HttpResponseRedirect("/modules-home/")
    elif task == "active":
        active = request.GET.get('id')
        moduleobj = Modules.objects.get(id=active)
        moduleobj.active = 2
        moduleobj.save()
        success = True
        msg = "Module Activated Successfully"
        return HttpResponseRedirect("/modules-home/")
    return render(request, "mastermodule/modules.html", locals())


#-------------------------------Task_Statuses--------------------------------#


@login_required(login_url="/login/")
def task_staus_details(request):
    task_statuses = Task_Statuses.objects.all()
    return render(request, "mastermodule/task-statuses-home.html", locals())


@login_required(login_url="/login/")
def task_statuses(request, task='None', id=None):
    msg = ''
    if task == "add":
        form = Task_StatusesForm()
        if request.method == "POST":
            form = Task_StatusesForm(request.POST)
            name = request.POST.get('name')
            if Task_Statuses.objects.filter(name=name):
                msg = "name already exists"
                return render(request, "mastermodule/task-statuses.html", locals())
            if form.is_valid():
                check = Task_Statuses.objects.filter(name=name)
                if not check:
                    task_statuses = Task_Statuses.objects.create(name=name)
                    added = True
                    msg = "successfully added"
                    return HttpResponseRedirect("/settings/statuses/")
                else:
                    msg = ''

    elif task == "edit":
        task_stausobj = Task_Statuses.objects.get(id=id)
        form = Task_StatusesForm(initial={'name': task_stausobj.name})
        if request.method == "POST":
            form = Task_StatusesForm(request.POST)
            if form.is_valid():
                name = request.POST.get('name')
                if Task_Statuses.objects.filter(name=name).exclude(id=id):
                    msg = "name already exists"
                    return render(request, "mastermodule/task-statuses.html", locals())
                task_stausobj.name = name
                task_stausobj.save()
                added = True
                success = True
            return HttpResponseRedirect("/settings/statuses/")

    elif task == "delete":
        id_delete = id
        task_stausobj = Task_Statuses.objects.get(id=id_delete)
        task_stausobj.active = 0
        task_stausobj.save()
        success = True
        return HttpResponseRedirect("/settings/statuses/")

    elif task == "active":
        id_active = id
        task_stausobj = Task_Statuses.objects.get(id=id_active)
        task_stausobj.active = 2
        task_stausobj.save()
        success = True
        return HttpResponseRedirect("/settings/statuses/")

    return render(request, "mastermodule/task-statuses.html", locals())

#---------------------------Task_Priorities----------------------------------#


@login_required(login_url="/login/")
def task_priorities_list(request):
    task_priorities_list = Task_priorities.objects.all()
    return render(request, "mastermodule/task-priorities-home.html", locals())


@login_required(login_url="/login/")
def task_priorities_details(request, task='None', id=None):
    msg = ''
    if task == "add":
        form = Task_PrioritiesForm()
        if request.method == "POST":
            form = Task_PrioritiesForm(request.POST)
            name = request.POST.get('name')
            color = request.POST.get('color')
            if form.is_valid():
                if Task_priorities.objects.filter(name=name):
                    msg = "Priority already exists."
                    return render(request, "mastermodule/task-priorities.html", locals())
                else:
                    task_priorities = Task_priorities.objects.create(name=name, color=color)
                    task_priorities = Task_priorities.objects.create(color=color)
                    added = True
                    msg = "successfully added"
                    return HttpResponseRedirect("/settings/task/priorities/")
    elif task == "edit":
        task_prioritiesobj = Task_priorities.objects.get(id=id)
        form = Task_PrioritiesForm(initial={
            'name': task_prioritiesobj.name,
            'color':task_prioritiesobj.color,})
        if request.method == "POST":
            form = Task_PrioritiesForm(request.POST)
            if form.is_valid():
                if Task_priorities.objects.filter(name=request.POST.get('name')).exclude(id=id):
                    msg = "Priority already exists."
                    return render(request, "mastermodule/task-priorities.html", locals())
                else:
                    task_prioritiesobj.name = request.POST.get('name')
                    task_prioritiesobj.color = request.POST.get('color')
                    task_prioritiesobj.save()
                    added = True
                    success = True
                    return HttpResponseRedirect("/settings/task/priorities/")
    elif task == "delete":
        id_delete = id
        task_prioritiesobj = Task_priorities.objects.get(id=id_delete)
        task_prioritiesobj.active = 0
        task_prioritiesobj.save()
        success = True
        return HttpResponseRedirect("/settings/task/priorities/")
    elif task == "active":
        id_active = id
        task_prioritiesobj = Task_priorities.objects.get(id=id_active)
        task_prioritiesobj.active = 2
        task_prioritiesobj.save()
        success = True
        return HttpResponseRedirect("/settings/task/priorities/")
    return render(request, "mastermodule/task-priorities.html", locals())


@login_required(login_url="/login/")
def addsettings(request):
    form = GeneralinfoForm()
    error = ''
    msg = ''
    nam = ''
    x = ''
    f = ''
    messages = ''
    if request.method == 'POST':
        form = GeneralinfoForm(request.POST, request.FILES)
        name = request.POST.get('name', '')
        if form.is_valid():
            f = form.save(commit=False)
            f.slug = name
            f.save()
            msg = "successfully saved"
            return HttpResponseRedirect("/Settings & Defaults/")
        else:
            error = "form error"
    return render(request, "mastermodul/add_settings.html", locals(),
                             context_instance=RequestContext(request))


@login_required(login_url="/login/")
def editsettings(request, id_edit):
    msg = ''
    settign = Generalinfo.objects.get(id=id_edit)
    form = GeneralinfoForm(instance=settign)
    if request.POST:
        form = GeneralinfoForm(request.POST, instance=settign)
        if form.is_valid():
            f = form.save(commit=False)
            if not Generalinfo.objects.filter(Intervals_Domain_Name=request.POST.get('Intervals_Domain_Name')).exclude(id=settign.id).exists():
                f.save()
                edit_done = True
                msg = "edited successfully"
                success = True
                return HttpResponseRedirect("/mastermodule/")
            else:
                msg = "Already Exists!!"
        else:
             msg='Invalid form'
    return render(request, "mastermodule/add_settings.html", locals())


@login_required(login_url="/login/")
def settings_and_defaults(request):
    settings = Generalinfo.objects.all()
    admin = UserProfile.objects.all()
    return render(request, "mastermodule/settings-and-default.html", locals())


#======================================Project_categorization==============#


@login_required(login_url="/login/")
def project_categorization_list(request):
    project_categorization_obj = Project_categorization.objects.all()
    return render(request, 'mastermodule/project-categorizations-home.html', locals())



@login_required(login_url="/login/")
def project_categorization_details(request, task='None', id=None):
    msg = ''
    if task == "add":
        form = Project_categorizationForm()
        if request.method == "POST":
            form = Project_categorizationForm(request.POST)
            name = request.POST.get('name')
            if form.is_valid():
                if Project_categorization.objects.filter(name=name):
                    msg = 'Category already exists.'
                    return render(request, "mastermodule/project-categorization.html", locals())
                else:
                    project_categorization = Project_categorization.objects.create(name=name)
                    added = True
                    msg = "successfully added"
                    return HttpResponseRedirect("/settings/project/categorizations/")
    elif task == "edit":
        project_categorization_obj = Project_categorization.objects.get(id=id)
        form = Project_categorizationForm(initial={'name': project_categorization_obj.name})
        if request.method == "POST":
            form = Project_categorizationForm(request.POST)
            if form.is_valid():
                name = request.POST.get('name')
                if Project_categorization.objects.filter(name=name).exclude(id=id):
                    msg = 'Category already exists.'
                    return render(request, "mastermodule/project-categorization.html", locals())
                else:
                    project_categorization_obj.name = name
                    project_categorization_obj.save()
                    added = True
                    success = True
                    return HttpResponseRedirect("/settings/project/categorizations/")
    elif task == "delete":
        id_delete = id
        project_categorization_obj = Project_categorization.objects.get(id=id_delete)
        project_categorization_obj.active = 0
        project_categorization_obj.save()
        success = True
        return HttpResponseRedirect("/settings/project/categorizations/")
    elif task == "active":
        id_active = id
        project_categorization_obj = Project_categorization.objects.get(id=id_active)
        project_categorization_obj.active = 2
        project_categorization_obj.save()
        success = True
        return HttpResponseRedirect("/settings/project/categorizations/")
    return render(request, "mastermodule/project-categorization.html", locals())


@login_required(login_url="/login/")
def resource_categorization_list(request):
    resource_categorization_obj = Resource_Categorization.objects.all()
    return render(request, "mastermodule/resource-categorizations-home.html", locals())


#=========================================Resource_Categorization=========#


@login_required(login_url="/login/")
def resource_categorizations_details(request, task=None, id=None):
    msg = ''
    form = ''
    if task == "add":
        form = Resource_CategorizationForm()
        if request.method == "POST":
            form = Resource_CategorizationForm(request.POST)
            name = request.POST.get('name')
            if form.is_valid():
                if Resource_Categorization.objects.filter(name=name):
                    msg = 'Resource categorization already exists.'
                    return render(request, "mastermodule/resource-categorizations-add.html", locals()) 
                else:
                    resource_categorization = Resource_Categorization.objects.create(name=name)
                    added = True
                    msg = "successfully added"
                    return HttpResponseRedirect("/settings/resource/categorizations/")
    elif task == "edit":
        id_edit = id
        resource_categorization_obj = Resource_Categorization.objects.get(id=id_edit)
        form = Resource_CategorizationForm(initial={'name': resource_categorization_obj.name})
        if request.method == "POST":
            form = Resource_CategorizationForm(request.POST)
            if form.is_valid():
                name = request.POST.get('name')
                if Resource_Categorization.objects.filter(name=name).exclude(id=id):
                    msg = 'Resource categorization already exists.'
                    return render(request, "mastermodule/resource-categorizations-add.html", locals()) 
                else:
                    resource_categorization_obj.name = name
                    resource_categorization_obj.save()
                    added = True
                    success = True
                    return HttpResponseRedirect("/settings/resource/categorizations/")
    elif task == "delete":
        id_delete = id
        resource_categorization_obj = Resource_Categorization.objects.get(id=id_delete)
        resource_categorization_obj.active = 0
        resource_categorization_obj.save()
        success = True
        return HttpResponseRedirect("/settings/resource/categorizations/")
    elif task == "active":
        id_active = id
        resource_categorization_obj = Resource_Categorization.objects.get(id=id_active)
        resource_categorization_obj.active = 2
        resource_categorization_obj.save()
        success = True
        return HttpResponseRedirect("/settings/resource/categorizations/")
    return render(request, "mastermodule/resource-categorizations-add.html", locals())




