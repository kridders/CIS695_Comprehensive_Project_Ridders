from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length=200)
    goal = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        through="ProjectMembership",
        related_name='projects'
    )

    def __str__(self):
        return self.title

class TeamMember(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="team_members")

    def __str__(self):
        return self.name


class ProjectInvitation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="invitations")
    email = models.EmailField()
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_invitations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="project_invitations")

    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(null=True)  

    def __str__(self):
        return f"{self.email} -> {self.project.title}"

class Task(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) 

    def __str__(self):
        return self.title
    
class Update(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="updates")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.title} - {self.created_at}"
class Document(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

   
class ProjectMembership(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MEMBER', 'Member'),
        ('VIEWER', 'Viewer'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER')

    class Meta:
        unique_together = ('user', 'project')
    
    def __str__(self):
        return f"{self.user.username} - {self.project.title} ({self.role})"
    
class AISuggestion(models.Model):
    SUGGESTION_TYPE_CHOICES = [
        ('TASK', 'Task'),
        ('DEADLINE', 'Deadline'),
        ('SUMMARY', 'Summary')
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name ="ai_suggestions")
    suggestion_type = models.CharField(max_length=20, choices=SUGGESTION_TYPE_CHOICES)
    content= models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.suggestion_type} suggestion"

class TaskComment(models.Model):
    task=models.ForeignKey('Task', on_delete=models.CASCADE)
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.task.title}"
    
class TaskAttachment(models.Model):
    task=models.ForeignKey('Task', on_delete=models.CASCADE, related_name="attachments")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='task_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name}" ({self.uploaded_by.username if self.uploaded_by else 'Unknown'})