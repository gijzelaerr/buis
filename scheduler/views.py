from django.views import generic
from .models import Repository
from django.views.generic.edit import CreateView


class RepositoryIndex(generic.ListView):
    model = Repository


class RepositoryDetail(generic.DetailView):
    model = Repository


class RepositoryCreate(CreateView):
    model = Repository
    fields = ['url']