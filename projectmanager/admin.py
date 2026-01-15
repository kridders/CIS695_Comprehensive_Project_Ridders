from django.contrib import admin
from .models import Project, TeamMember, Task, Update, Document, AISuggestion

# Register your models here.
admin.site.register(Project)
admin.site.register(TeamMember)
admin.site.register(Task)
admin.site.register(Update)
admin.site.register(Document)
admin.site.register(AISuggestion)
