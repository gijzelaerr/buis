from django.views.generic import ListView, DetailView
from .models import Repository
from .serializers import RepositorySerializer
from django.views.generic.edit import CreateView
from rest_framework.generics import ListCreateAPIView


class RepositoryIndex(ListView):
    model = Repository


class RepositoryDetail(DetailView):
    model = Repository


class RepositoryCreate(CreateView):
    model = Repository
    fields = ['url']


class RepositoryListCreate(ListCreateAPIView):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer