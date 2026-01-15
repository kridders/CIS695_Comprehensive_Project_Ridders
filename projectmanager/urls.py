from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),

    path('projects/new/', views.create_project, name='create_project'),
    path('projects/<int:project_id>/', views.project_dashboard, name='project_dashboard'),

    path(
        'projects/<int:project_id>/tasks/new/',
        views.create_task,
        name='create_task'
    ),

    path(
        'task/<int:task_id>/status/',
        views.update_task_status,
        name='update_task_status'
    ),
]
