from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Project, Location, Remark
from .forms import ProjectForm

from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from xhtml2pdf import pisa
import os
import csv


###################################
def createCSV(request):
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        if project_id == 'all':
            projects = Project.objects.all()
        else:
            try:
                project = Project.objects.get(id=project_id)
                projects = [project]
            except Project.DoesNotExist:
                projects = []
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="projects.csv"'

        writer = csv.writer(response)
        writer.writerow(['Project Name', 'Location', 'Total Amount', 'Payments to Date', 'Description'])
        
        for project in projects:
            writer.writerow([project.name, project.location, project.totalamount, project.payments_todate, project.description])

        return response
    else:
        return HttpResponse("Method not allowed")



############################################



# Generate a PDF file
def createPDF(request):
    template_path = 'base/pdf_template.html'

    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        if project_id == 'all':
            projects = Project.objects.all()
        else:
            try:
                project = Project.objects.get(id=project_id)
                projects = [project]
            except Project.DoesNotExist:
                projects = []
    else:
        projects = []

    # Render the template with the project data
    context = {'projects': projects}
    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF file
    file_path = os.path.join(settings.MEDIA_ROOT, 'report.pdf')
    with open(file_path, 'w+b') as file:
        pisa.CreatePDF(html, dest=file)

    # Return the PDF file as a response
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=report.pdf'
        return response


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        location = request.POST.get('location')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request,'Username or Password is incorrect')
    context = {'page':page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')


# NEW CONTENT
from .forms import UserCreationFormExtended

# ...

def registerPage(request):
    form = UserCreationFormExtended()

    if request.method == 'POST':
        form = UserCreationFormExtended(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')
    return render(request, 'base/login_register.html', {'form': form})


######################################################################
# def registerPage(request):
#     form = UserCreationForm()

#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.username = user.username.lower()
#             user.save()
#             login(request, user)
#             return redirect('home')
#         else:
#             messages.error(request, 'An error occured during registration')
#     return render(request,'base/login_register.html', {'form':form})
##################################################################

@login_required(login_url='login')
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    projects = Project.objects.filter(
        Q(location__name__icontains=q) |
        Q(name__icontains = q) 
        #Q(host__name__icontains = q)
        ) 

    locations = Location.objects.all() 
    project_count = projects.count()
    remarks = Remark.objects.all().filter(Q(project__location__name__icontains=q))

    context = {'projects':projects, 'locations':locations, 'project_count':project_count, 'remarks':remarks}
    return render(request, 'base/home.html', context)

def project(request, pk):
    project = Project.objects.get(id=pk)
    remarks = project.project_content_type.all()
    authorized_users = project.authorized_users.all()

    if request.method== "POST":
        remark = Remark.objects.create(
            user=request.user,
            project=project,
            body=request.POST.get('body')
        )
        project.authorized_users.add(request.user)
        return redirect('project', pk=project.id)
    
    context = {'project':project, 'remarks':remarks, 'authorized_users':authorized_users}
    return render(request, 'base/project.html',context)

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    projects = user.project_set.all()
    remarks = Remark.objects.filter(user=user)  
    locations = Location.objects.all()
    context = {'user':user, 'projects':projects, 'remarks':remarks,'locations':locations}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createProject(request):
    form = ProjectForm()

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.host = request.user
            project.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/project_form.html', context)

@login_required(login_url='login')
def updateProject(request,pk):
    project = Project.objects.get(id=pk)
    form = ProjectForm(instance=project)

    if request.user != project.host:
        return HttpResponse('Invalid User')

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form':form}
    return render(request,'base/project_form.html', context)

@login_required(login_url='login')
def deleteProject(request, pk):
    project = Project.objects.get(id=pk)

    if request.user != project.host:
        return HttpResponse('Invalid User')
    
    if request.method == 'POST':
        project.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':project})

@login_required(login_url='login')
def deleteRemark(request, pk):
    remark = Remark.objects.get(id=pk)

    if request.user != remark.user:
        return HttpResponse('Invalid User')
    
    if request.method == 'POST':
        remark.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':remark})