from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length=200)
    goal = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()

    members = models.ManyToManyField(User, related_name='projects')

    def __str__(self):
        return self.title

class TeamMember(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="team_members")

    def __str__(self):
        return self.name
    
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
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Update ( {self.created_at.date()})"

class Document(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
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
    