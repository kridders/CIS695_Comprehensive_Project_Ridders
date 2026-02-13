from django.core.management.base import BaseCommand
from projectmanager.models import Project, ProjectMembership

class Command(BaseCommand):
    help = 'Überträgt alle Mitglieder in ProjectMembership'

    def handle(self, *args, **kwargs):
        for project in Project.objects.all():
            for user in project.members.all():
                # get_or_create sorgt dafür, dass keine Duplikate entstehen
                membership, created = ProjectMembership.objects.get_or_create(
                    project=project,
                    user=user,
                    defaults={'role': 'MEMBER'}  # nur beim ersten Mal
                )
                if created:
                    self.stdout.write(f"{user.username} wurde zu {project.title} hinzugefügt")
                else:
                    self.stdout.write(f"{user.username} ist bereits Mitglied von {project.title}")

        self.stdout.write(self.style.SUCCESS('Migration abgeschlossen!'))
