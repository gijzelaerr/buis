from django.urls import path, re_path

from . import views

app_name = 'scheduler'


urlpatterns = [
    path('', views.RepositoryIndex.as_view(), name='repo_list'),
    path('<int:pk>/', views.RepositoryDetail.as_view(), name='repo_detail'),
    path('create/', views.RepositoryCreate.as_view(), name='repo_create'),
    path('delete/<int:pk>/', views.RepositoryDelete.as_view(), name='repo_delete'),
    path('update/<int:pk>/', views.repository_update, name='repo_update'),

    path('api/repository/', views.RepositoryListCreate.as_view()),


    re_path(r'workflow/detail/(?P<run_id>[0-9a-f]{32})/$', views.workflow_detail, name='workflow_detail'),
    path('workflow/list/', views.workflow_list, name='workflow_list'),
    re_path(r'workflow/delete/(?P<run_id>[0-9a-f]{32})/$', views.workflow_delete, name='workflow_delete'),

    path('workflow/run/<int:repo_id>/<str:cwl_path>/', views.workflow_run, name='workflow_run'),
]
