from .models import ProjectMembership, ProjectInvitation

def invitations_processor(request):
    if request.user.is_authenticated:
        return {
            "pending_invitations": ProjectInvitation.objects.filter(
                email=request.user.email,
                accepted__isnull=True
            )
        }
    return {}

def project_role_processor(request):
    def get_role(project):
        if not request.user.is_authenticated:
            return None
        try:
            return ProjectMembership.objects.get(
                user=request.user,
                project=project
            ).role
        except ProjectMembership.DoesNotExist:
            return None

    return {
        "get_project_role": get_role
    }