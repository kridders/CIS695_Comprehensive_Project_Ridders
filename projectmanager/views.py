from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task, ProjectInvitation, ProjectMembership, TaskComment, TaskAttachment, Update
from .forms import TaskForm, ProjectForm, AddMemberForm, CustomUserCreationForm, TaskAttachmentForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponseForbidden
from django.http import JsonResponse


#View to create task
@login_required
def create_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    Update.objects.create(
        project=project,
        user=request.user,
        text="created task '{task.title}'"
    )

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

    if task.assigned_to != request.user:
        return HttpResponseForbidden("You are not allowed to change this task's status.")

    if request.method == "POST":
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()

    Update.objects.create(
    project=task.project,
    user=request.user,
    text=f"changed status of '{task.title}' to {task.status}"
)

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
@login_required
def project_dashboard(request, project_id):
    project = get_object_or_404(Project, id=project_id, members=request.user)

    tasks = project.tasks.all()
    updates = project.updates.order_by('-created_at')[:5]
    projects = request.user.projects.all()

    memberships = ProjectMembership.objects.filter(project=project, user__isnull=False)

    try:
        user_membership = memberships.get(user=request.user)
        user_role = user_membership.role
    except ProjectMembership.DoesNotExist:
        user_role = None

    # -------------------------
    # 🔽 FILTER & SORT LOGIK
    # -------------------------

    status_filter = request.GET.get("status")
    assigned_filter = request.GET.get("assigned")
    sort = request.GET.get("sort")

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    if assigned_filter:
        tasks = tasks.filter(assigned_to__id=assigned_filter)

    if sort == "deadline":
        tasks = tasks.order_by("deadline")
    elif sort == "deadline_desc":
        tasks = tasks.order_by("-deadline")
    elif sort == "status":
        tasks = tasks.order_by("status")

    # -------------------------

    context = {
        'project': project,
        'tasks': tasks,
        'updates': updates,
        'projects': projects,
        'memberships': memberships,
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

def get_project_role(user, project):
    membership = ProjectMembership.objects.filter(
        user=user,
        project=project
    ).first()
    return membership.role if membership else None

@login_required
def change_role(request, project_id, user_id):
    project = get_object_or_404(Project, id=project_id)

    if not is_project_admin(request.user, project):
        return HttpResponseForbidden("Not allowed")
    
    membership = get_object_or_404(
        ProjectMembership,
        project=project,
        user_id = user_id
    )

    if request.method == "POST":
        new_role = request.POST.get("role")
        if new_role in ["ADMIN", "MEMBER", "VIEWER"]:
            membership.role = new_role
            membership.save()
        return redirect("project_dashboard", project_id=project.id)

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Nur der zugewiesene User darf löschen
    if task.assigned_to != request.user:
        return HttpResponseForbidden("You are not allowed to delete this task.")

    if request.method == "POST":
        task.delete()
        return redirect('project_dashboard', project_id=task.project.id)        

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Prüfen, ob der User im Projekt ist
    if not task.project.memberships.filter(user=request.user).exists():
        return HttpResponseForbidden("You cannot view this task.")

    # Render nur für AJAX (Modal)
    return render(request, 'projectmanager/task_detail_partial.html', {
        'task': task,
        'user_in_project': True,
    })


@login_required
def add_task_comment(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if not task.project.memberships.filter(user=request.user).exists():
        return HttpResponseForbidden("You cannot comment on this task.")

    Update.objects.create(
        project=task.project,
        user=request.user,
        text=f"commented on '{task.title}'"
    )
    if request.method == "POST":
        text = request.POST.get('text')
        if text:
            TaskComment.objects.create(task=task,user=request.user, text=text)
    return redirect('task_detail', task_id=task.id)

@login_required
def add_task_attachment(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Nur Projektmitglieder dürfen hochladen
    if not task.project.memberships.filter(user=request.user).exists():
        return HttpResponseForbidden("You cannot upload files to this task.")

    if request.method == "POST":
        form = TaskAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.task = task
            attachment.uploaded_by = request.user
            attachment.save()

            # Wenn AJAX, gib direkt die HTML-Zeile zurück
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = f'''
                <li style="margin-bottom: 0.5rem; display:flex; align-items:center; justify-content:space-between;">
                    <span style="display:flex; align-items:center; max-width: calc(100% - 50px);">
                        📎
                        <a href="{attachment.file.url}" download 
                           class="attachment-name" 
                           style="margin-left:0.3rem; word-break: break-word; text-decoration:none; color:#333;">
                            {attachment.file.name.split("/")[-1].rsplit(".",1)[0]}
                        </a>
                    </span>
                    <button type="button" 
                            class="delete-attachment-btn" 
                            data-attachment-id="{attachment.id}" 
                            style="border:none; background:none; cursor:pointer; color:red;" 
                            title="Delete Attachment">
                        🗑️
                    </button>
                </li>
                '''
                return JsonResponse({'success': True, 'html': html})
            
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskAttachmentForm()

    Update.objects.create(
        project=task.project,
        user=request.user,
        text="uploaded attachment to '{task.title}'"
    )
    return render(request, 'projectmanager/task_detail.html', {
        'task': task,
        'attachment_form': form,
        'user_in_project': task.project.memberships.filter(user=request.user).exists()
    })


@login_required
def delete_task_attachment(request, attachment_id):
    attachment = get_object_or_404(TaskAttachment, id=attachment_id)
    task = attachment.task

    # Nur Projektmitglieder dürfen löschen
    if not task.project.memberships.filter(user=request.user).exists():
        return HttpResponseForbidden("You cannot delete this attachment.")

    attachment.file.delete(save=False)  # Datei löschen
    attachment.delete()  # Datenbankeintrag löschen

    # Wenn AJAX, nur den Erfolg zurückgeben
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'attachment_id': attachment_id})
    
    # Sonst klassisch redirect
    return redirect('task_detail', task_id=task.id)


@login_required
def clear_updates(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    membership = ProjectMembership.objects.get(project=project, user=request.user)

    if membership.role != "ADMIN":
        return HttpResponseForbidden()
    
    project.updates.all().delete()
    return redirect("project_dashboard", project.id)
