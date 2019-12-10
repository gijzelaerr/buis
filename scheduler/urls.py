from django.urls import path

from scheduler.views import repository
from scheduler.views import workflow
from scheduler.views import viewer

app_name = 'scheduler'


urlpatterns = [
    path('', repository.RepositoryIndex.as_view(), name='repo_list'),
    path('<int:pk>/', repository.RepositoryDetail.as_view(), name='repo_detail'),
    path('create/', repository.RepositoryCreate.as_view(), name='repo_create'),
    path('delete/<int:pk>/', repository.RepositoryDelete.as_view(), name='repo_delete'),
    path('update/<int:pk>/', repository.repository_update, name='repo_update'),

    path('workflow/list/', workflow.WorkflowList.as_view(), name='workflow_list'),
    path('workflow/create/<int:repo_id>/<str:cwl_path>/', workflow.WorkflowCreate.as_view(), name='workflow_create'),
    path(r'workflow/detail/<int:pk>/', workflow.WorkflowDetail.as_view(), name='workflow_detail'),
    path(r'workflow/delete/<int:pk>/', workflow.WorkflowDelete.as_view(), name='workflow_delete'),
    path(r'workflow/restart/<int:pk>/', workflow.workflow_restart, name='workflow_restart'),

    # intermediate workflow creation steps
    path('workflow/run/<int:repo_id>/<str:cwl_path>/', workflow.workflow_visualize, name='workflow_visualize'),
    path('workflow/run/<int:repo_id>/<str:cwl_path>/', workflow.workflow_run, name='workflow_run'),
    path('workflow/job/<int:repo_id>/<str:cwl_path>/', workflow.workflow_job, name='workflow_job'),
    path('workflow/parse/<int:repo_id>/<str:cwl_path>/', workflow.workflow_parse, name='workflow_parse'),

    # Rest API
    path('api/repository/', repository.RepositoryListCreate.as_view()),

    path('<int:pk>/fits/<str:path>/', viewer.FitsView.as_view(), name='viewer_fits'),
    path('<int:pk>/text/<str:path>/', viewer.TextView.as_view(), name='viewer_text'),
    path('something/<int:pk>/<str:path>/', viewer.SomethingView.as_view(), name='viewer_guesstype'),
    path('js9/<int:pk>/<str:path>/', viewer.Js9View.as_view(), name='viewer_js9'),



]




