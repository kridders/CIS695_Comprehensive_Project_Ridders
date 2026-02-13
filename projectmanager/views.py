from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task, ProjectInvitation, ProjectMembership
from .forms import TaskForm, ProjectForm, AddMemberForm, CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponseForbidden

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

            # 🔥 Ersteller wird automatisch ADMIN
            ProjectMembership.objects.create(
                user=request.user,
                project=project,
                role='ADMIN'
            )

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

    tasks = project.tasks.all()
    updates = project.updates.order_by('-created_at')[:5]
    projects = request.user.projects.all()

    memberships = ProjectMembership.objects.filter(project=project)

    try:
        user_membership = memberships.get(user=request.user)
        user_role = user_membership.role
    except ProjectMembership.DoesNotExist:
        user_role = None
    context = {
        'project': project,
        'tasks': tasks,
        'updates': updates,
        'projects': projects,
        'memberships': memberships,  # ← verwenden wir im Template
        'user_role': user_role,
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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('project_list')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'projectmanager/register.html', {'form': form})

@login_required
def add_member(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # 🔒 Nur Admin darf Leute hinzufügen
    if not is_project_admin(request.user, project):
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        email = request.POST.get("email")

        # Prüfen, ob schon ein Mitglied mit dieser Email existiert
        if ProjectMembership.objects.filter(user__email=email, project=project).exists():
            return render(request, "projectmanager/add_member.html", {
                "project": project,
                "error": "User is already a member"
            })

        # Einladung erstellen, egal ob User existiert oder nicht
        invitation = ProjectInvitation.objects.create(
            project=project,
            email=email,
            invited_by=request.user
        )

        messages.success(request, f"Invitation sent to {email}.")
        return redirect("project_dashboard", project_id=project.id)

    return render(request, "projectmanager/add_member.html", {
        "project": project
    })


@login_required
def invite_user(request, project_id):
    project = get_object_or_404(Project, id=project_id, members=request.user)

    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            ProjectInvitation.objects.create(
                project=project,
                invited_user=user,
                invited_by=request.user
            )
            messages.success(request, "Invitation sent.")
        else:
            messages.error(request, "User not found.")

    return redirect('project_dashboard', project_id=project.id)

@login_required
def handle_invitation(request, invitation_id, action):
    invitation = get_object_or_404(
        ProjectInvitation,
        id=invitation_id,
        invited_user=request.user
    )

    if action == "accept":
        invitation.accepted = True
        invitation.project.members.add(request.user)
    elif action == "reject":
        invitation.accepted = False

    invitation.save()
    return redirect('project_list')

def is_project_admin(user, project):
    return ProjectMembership.objects.filter(
        user=user,
        project=project,
        role='ADMIN'
    ).exists()

@login_required
def decline_invitation(request, invitation_id):
    invitation = get_object_or_404(ProjectInvitation, id=invitation_id, email=request.user.email)
    # Einladung ablehnen = löschen
    invitation.delete()
    messages.success(request, f"Invitation to {invitation.project.title} declined.")
    return redirect("project_list")


@login_required
def accept_invitation(request, invitation_id):
    invitation = get_object_or_404(ProjectInvitation, id=invitation_id, email=request.user.email)
    
    # Mitgliedschaft erstellen
    ProjectMembership.objects.create(
        user=request.user,
        project=invitation.project,
        role='MEMBER'
    )
    
    # Einladung löschen
    invitation.delete()
    
    messages.success(request, f"You have joined {invitation.project.title}.")
    return redirect("project_list")

@login_required
def remove_member(request, project_id, user_id):
    project = get_object_or_404(Project, id=project_id)

    # Nur Admin darf
    if not is_project_admin(request.user, project):
        return HttpResponseForbidden("Not allowed")

    # Admin darf sich selbst nicht entfernen
    if request.user.id == user_id:
        return HttpResponseForbidden("You cannot remove yourself")

    membership = get_object_or_404(
        ProjectMembership,
        project=project,
        user_id=user_id
    )

    membership.delete()

    return redirect('project_dashboard', project_id=project.id)

