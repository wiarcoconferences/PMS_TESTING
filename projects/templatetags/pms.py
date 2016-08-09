from django import template
register = template.Library()

from people.models import *
from projects.models import Project
from milestones.models import *
from tasks.models import *

@register.filter
def get_client_list(request):

    user = request.user.id
    userprofile_obj = UserProfile.objects.get(user=user)
    if userprofile_obj.access_level == '1':
        client_list = Client.objects.all()
        return client_list
    else:
        return (i.client for i in userprofile_obj.project.all())


@register.filter
def get_project_list(request):

    user = request.user.id
    userprofile_obj = UserProfile.objects.get(user=user)
    if userprofile_obj.access_level == '1':
        projects_list = Project.objects.all()
        return projects_list
    else:
        project_list = userprofile_obj.project.all()
        return project_list


@register.filter
def get_milestones_list(request):

    user = request.user.id
    userprofile_obj = UserProfile.objects.get(user=user)
    if userprofile_obj.access_level == '1':
        milestone_list = Milestone.objects.all()
        return milestone_list
    else:
        milestone_list = userprofile_obj.get_milestones_list
        print milestone_list
        return milestone_list


@register.filter
def get_available_tasks(request):

    user = request.user.id
    userprofile_obj = UserProfile.objects.get(user=user)
    if userprofile_obj.access_level == '1':
        tasks_list = Tasks.objects.all()
        return tasks_list
    else:
        tasks_list = Tasks.objects.filter(owned_by__user=user)
        print tasks_list
        return tasks_list


@register.filter
def get_dict(request):
#    import ipdb; ipdb.set_trace();
    #create a dict with the years and months:events 
    times_list = AddTime.objects.all().order_by('-created_on')
    time_dict = {}
    for i in range(times_list[0].created_on.year, times_list[len(times_list)-1].created_on.year-1, -1):
        time_dict[i] = {}
        for month in range(1,13):
            time_dict[i][month] = []
    for times in times_list:
        time_dict[times.created_on.year][times.created_on.month].append(times)
    #this is necessary for the years to be sorted
    times_sorted_keys = list(reversed(sorted(time_dict.keys())))
    list_times = []
    for key in times_sorted_keys:
        adict = {key:time_dict[key]}
        list_times.append(adict)
    return list_times


@register.filter
def get_followers(request):
    userprofile_ids = []
    user = request.user.id
    userprofile_obj = UserProfile.objects.get(user=user)
    if userprofile_obj.access_level == '1':
        task_followers = UserProfile.objects.all()
        return task_followers
    else:
        project = userprofile_obj.project.all()
        project_ids = [i.id for i in userprofile_obj.project.all()]
        #project = Project.objects.filter(id__in=project_ids))
        usp = UserProfile.objects.filter(project__id__in = project_ids)
        for j in usp:
            userprofile_ids.append(j.id)
        task_followers=UserProfile.objects.filter(id__in = list(set(userprofile_ids)))
        return task_followers

@register.filter
def get_checked_user(uspfId, proId):
    try:
        project = Project.objects.get(pk = int(proId))
        user_list = project.get_user_profile().values_list('pk', flat = True)
        if int(uspfId) in user_list:
            objid = int(uspfId)
        else:
            objid = None
    except:
        pass
    return objid








