from django.urls import path
from . import views

urlpatterns = [
    # Homepage: A logged in user sees all of his projects
    path('', views.project_list, name='project_list'),

    # Create Project
    path('projects/new/', views.create_project, name='create_project'),

    # Dashboard of a Project
    path('projects/<int:project_id>/', views.project_dashboard, name='project_dashboard'),

    # Create new Task of Project
    path('projects/<int:project_id>/tasks/new/', views.create_task, name='create_task'),

    # Update Status of Task
    path('task/<int:task_id>/status/', views.update_task_status, name='update_task_status'),

    # Registration of new user
    path('register/', views.register, name='register'),

    #Add project members
    path('projects/<int:project_id>/add-member/', views.add_member, name='add_member'),

    #Accept / Deline invitations
    path("invitations/accept/<int:invitation_id>/", views.accept_invitation, name="accept_invitation"),
    path("invitations/decline/<int:invitation_id>/", views.decline_invitation, name="decline_invitation"),

    #Remove Members from projects
    path('projects/<int:project_id>/remove/<int:user_id>/',views.remove_member, name='remove_member')
]