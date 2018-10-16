from django.urls import path

from . import views

app_name = 'scheduler'
urlpatterns = [
    path('', views.RepositoryIndex.as_view(), name='index'),
    path('<int:pk>/', views.RepositoryDetail.as_view(), name='detail'),
    path('create/', views.RepositoryCreate.as_view(), name='create')
]