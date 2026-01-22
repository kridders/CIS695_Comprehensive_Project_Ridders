from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task
from .forms import TaskForm, ProjectForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db import models
from django.contrib.auth import login

#View to create task
@login_required
def create_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            return redirect('project_dashboard', project_id=project.id)
    else:
        form = TaskForm(project=project)

    return render(request, 'projectmanager/create_task.html', {'form': form, 'project': project})

#view to change status of task
@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()

    return redirect(
        'project_dashboard',
        project_id=task.project.id
    )

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            project.members.add(request.user)
            return redirect(
                'project_dashboard',
                project_id=project.id
            )
    else:
        form = ProjectForm()

    return render(
        request,
        'projectmanager/create_project.html',
        {'form': form}
    )

@login_required
def project_dashboard(request, project_id):
    project = get_object_or_404(Project, id=project_id, members=request.user)
    
    # 🔹 Nur Tasks, die entweder keinem Benutzer zugewiesen sind oder dem aktuellen User
    tasks = project.tasks.all()

    updates = project.updates.order_by('-created_at')[:5]
    projects = request.user.projects.all()

    context = {
        'project': project,
        'tasks': tasks,
        'updates': updates,
        'projects': projects,
    }
    return render(request, 'projectmanager/project_dashboard.html', context)

@login_required
def project_list(request):
    projects = request.user.projects.all()
    
    return render(
        request,
        'projectmanager/project_list.html',
        {'projects': projects}
    )



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('project_list')
    else:
        form = UserCreationForm()
    
    return render(request, 'projectmanager/register.html', {'form': form})
