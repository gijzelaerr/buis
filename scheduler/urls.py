from django.urls import path

from . import views

app_name = 'scheduler'


urlpatterns = [
    path('', views.RepositoryIndex.as_view(), name='repo_list'),
    path('<int:pk>/', views.RepositoryDetail.as_view(), name='repo_detail'),
    path('create/', views.RepositoryCreate.as_view(), name='repo_create'),
    path('delete/<int:pk>/', views.RepositoryDelete.as_view(), name='repo_delete'),
    path('update/<int:pk>/', views.repository_update, name='repo_update'),

    path('workflow/list/', views.WorkflowList.as_view(), name='workflow_list'),
    path('workflow/create/<int:repo_id>/<str:cwl_path>/', views.WorkflowCreate.as_view(), name='workflow_create'),
    path(r'workflow/detail/<int:pk>/', views.WorkflowDetail.as_view(), name='workflow_detail'),
    path(r'workflow/delete/<int:pk>/', views.WorkflowDelete.as_view(), name='workflow_delete'),

    # intermediate workflow creation steps
    path('workflow/run/<int:repo_id>/<str:cwl_path>/', views.workflow_run, name='workflow_run'),
    path('workflow/job/<int:repo_id>/<str:cwl_path>/', views.workflow_job, name='workflow_job'),
    path('workflow/parse/<int:repo_id>/<str:cwl_path>/', views.workflow_parse, name='workflow_parse'),

    # Rest API
    path('api/repository/', views.RepositoryListCreate.as_view()),

]
