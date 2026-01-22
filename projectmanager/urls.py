from django.urls import path
from . import views

urlpatterns = [
    # Startseite: Projektliste des angemeldeten Users
    path('', views.project_list, name='project_list'),

    # Neues Projekt erstellen
    path('projects/new/', views.create_project, name='create_project'),

    # Dashboard eines Projekts
    path('projects/<int:project_id>/', views.project_dashboard, name='project_dashboard'),

    # Neue Task innerhalb eines Projekts erstellen
    path('projects/<int:project_id>/tasks/new/', views.create_task, name='create_task'),

    # Status einer Task ändern
    path('task/<int:task_id>/status/', views.update_task_status, name='update_task_status'),

    path('register/', views.register, name='register')
]