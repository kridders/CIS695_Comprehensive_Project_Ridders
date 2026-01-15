from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task
from .forms import TaskForm, ProjectForm

#View to create task
def create_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)


    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            return redirect('project_dashboard', project_id=project.id)
    else:
        form = TaskForm()
    return render(request, 'projectmanager/create_task.html', {'form': form, 'project' : project})

#view to change status of task
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

def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
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

def project_dashboard(request, project_id):

    project = get_object_or_404(Project, id=project_id)

    tasks = project.tasks.all()

    updates = project.updates.order_by('-created_at')[:5]

    projects = Project.objects.all()

    context = {
        'project': project,
        'tasks': tasks,
        'updates': updates,
        'projects': projects, 
    }

    return render(request, 'projectmanager/project_dashboard.html', context)

def project_list(request):
    projects = Project.objects.all()
    
    return render(
        request,
        'projectmanager/project_list.html',
        {'projects': projects}
    )

