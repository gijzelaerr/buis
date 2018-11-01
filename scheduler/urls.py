from django.urls import path, re_path

from . import views

app_name = 'scheduler'


urlpatterns = [
    path('', views.RepositoryIndex.as_view(), name='index'),
    path('<int:pk>/', views.RepositoryDetail.as_view(), name='detail'),
    path('create/', views.RepositoryCreate.as_view(), name='create'),

    path('api/repository/', views.RepositoryListCreate.as_view()),

    re_path(r'jobdetail/(?P<run_id>[0-9a-f]{32})/$', views.job_detail, name='job_detail'),
    path('joblist/', views.job_list, name='job_list'),
]