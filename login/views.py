from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import render, render_to_response
from django.core.paginator  import Paginator,InvalidPage, EmptyPage
from django.http import HttpResponse,HttpResponseRedirect
from models import *
from forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import login as auth_login

def main(request):
    """ Main listing."""
    reg = Register.objects.all()
    return render_to_response("login/login.html",locals())

def signup(request):
    form = NameForm()
    error = ''
    msg = ''
    usr = ''
    f = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        retypepassword = request.POST.get('retypepassword')
        email = request.POST.get('email')
        form = NameForm(request.POST)
        if form.is_valid():
            if password == retypepassword:
                try:
                    usr = User.objects.get(username=username)
                except:
                    pass 
                if not usr:
                    usr = User.objects.create_user(username=username,password=password,email=email)
                    f = form.save()
                    msg = "Successfully Registered."
                    return HttpResponseRedirect("/login/")
                else:
                    msg = "user exisit"
            else:
                msg = "password not matches"
    else:
        form = NameForm()
    return render(request,"login/signup.html", locals())
    
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
                return HttpResponseRedirect('/main/')
            else:
                msg = 'your account is not active'
        else:
             msg = 'your username and password were incorrect.'
    return render(request,"login/auth.html",locals())

def mains(request):
    user = request.user
    return render(request,"myinterval/main.html",locals())


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/')
# Create your views here.
