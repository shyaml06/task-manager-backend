from django.urls import path
from .views import (
    Listprojectview, Createprojectview, CreateTask, ProjectsTaskView, 
    DashboardAnalyticsView, UpdateTaskStatusView, AssignTaskView, 
    AssignableUsersView, GenerateAIWorkflowView, GetProjectsView
)

urlpatterns = [
    path('',Listprojectview.as_view()),
    path('add/',Createprojectview.as_view()),
    path('task/add/',CreateTask.as_view()),
    path("<int:project_id>/tasks/", ProjectsTaskView.as_view(), name="project-tasks"),    
    path("<int:project_id>/ai-workflow/", GenerateAIWorkflowView.as_view(), name="ai-workflow"),
    path("analytics/",DashboardAnalyticsView.as_view()),
    path('task/<int:task_id>/update/', UpdateTaskStatusView.as_view(), name='update-task-status'),
    path('task/<int:task_id>/assign/', AssignTaskView.as_view(), name='assign-task'),
    path('users/assignable/', AssignableUsersView.as_view(), name='assignable-users'),
    path("test/", GetProjectsView.as_view()),
    
    
]