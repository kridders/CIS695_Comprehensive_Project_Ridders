from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('projects/<int:project_id>/remove/<int:user_id>/',views.remove_member, name='remove_member'),

    #Change roles of Team Members
    path('projects/<int:project_id>/change_role/<int:user_id>/', views.change_role, name="change_role"),

    #Delete Task
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),

    #Task Details
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),

    #Add Comments
    path('tasks/<int:task_id>/add_comment/', views.add_task_comment, name='add_task_comment'),

    #Add Attachment
    path('tasks/<int:task_id>/add_attachment/', views.add_task_attachment, name='add_task_attachment'),

    #Update task
    path('tasks/<int:task_id>/update-status/', views.update_task_status, name="update_task_status"),

    #Delete Attachment
    path('attachments/<int:attachment_id>/delete/', views.delete_task_attachment, name='delete_task_attachment'),

    #Clear Activity log
    path("project/<int:project_id>/clear-updates/", views.clear_updates, name="clear_updates")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)