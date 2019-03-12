from os import listdir

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView, DetailView, CreateView
from rest_framework.generics import ListCreateAPIView

from scheduler.models import Repository, RepositoryStateChange
from scheduler.serializers import RepositorySerializer
from scheduler.tasks import checkout, update
from scheduler.util import list_files


class RepositoryDelete(LoginRequiredMixin, DeleteView):
    model = Repository
    success_url = reverse_lazy('scheduler:repo_list')


class RepositoryListCreate(LoginRequiredMixin, ListCreateAPIView):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer


class RepositoryIndex(LoginRequiredMixin, ListView):
    model = Repository

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = 'repo'
        return context


class RepositoryDetail(LoginRequiredMixin, DetailView):
    model = Repository

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ls'] = listdir(self.object.path())
        context['cwl_files'] = list_files(self.object.path())
        return context


class RepositoryCreate(LoginRequiredMixin, CreateView):
    model = Repository
    fields = ['url']
    success_url = reverse_lazy('scheduler:repo_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        rsc = RepositoryStateChange(repository=self.object, state=RepositoryStateChange.ADDED)
        rsc.save()
        checkout.delay(pk=self.object.id)
        return response


@login_required
def repository_update(_, pk):
    repo = Repository.objects.get(pk=pk)
    repo.set_state(RepositoryStateChange.OUTDATED)
    repo.save()
    update.delay(pk=pk)
    return redirect('scheduler:repo_list')
