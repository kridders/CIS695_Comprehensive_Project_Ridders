from django import template
from projectmanager.models import ProjectMembership

register = template.Library()

@register.filter
def project_role(user, project):
    try:
        return ProjectMembership.objects.get(
            user=user,
            project=project
        ).role
    except ProjectMembership.DoesNotExist:
        return None