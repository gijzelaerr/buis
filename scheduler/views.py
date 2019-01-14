from logging import getLogger
from os import listdir, path
from django.views.generic import ListView, DetailView, DeleteView
from .models import Repository, RepositoryStateChange
from .serializers import RepositorySerializer
from django.views.generic.edit import CreateView
from rest_framework.generics import ListCreateAPIView
from wes_client.util import WESClient
from django.conf import settings
from requests.exceptions import ConnectionError
from django.http import HttpResponseServerError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .tasks import update, checkout


logger = getLogger(__name__)


class RepositoryIndex(ListView):
    model = Repository


class RepositoryDetail(DetailView):
    model = Repository

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ls'] = listdir(self.object.path())
        return context


class RepositoryCreate(CreateView):
    model = Repository
    fields = ['url']
    success_url = reverse_lazy('scheduler:repo_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        rsc = RepositoryStateChange(repository=self.object, state=RepositoryStateChange.ADDED)
        rsc.save()
        return response


class RepositoryDelete(DeleteView):
    model = Repository
    success_url = reverse_lazy('scheduler:repo_list')


class RepositoryListCreate(ListCreateAPIView):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer


def repository_update(repo_id):
    repo = Repository.objects.get(pk=repo_id)
    update.delay(pk=repo_id)
    return redirect('scheduler:repo_detail', repo_id)


def workflow_run(request, repo_id, cwl_path):
    client = WESClient(service={'auth': settings.WES_AUTH,
                                'proto': settings.WES_PROTO,
                                'host': settings.WES_HOST})

    repo = Repository.objects.get(pk=repo_id)

    full_cwl_path = path.abspath(path.join(repo.path(), cwl_path))
    assert(full_cwl_path.startswith(repo.path()))
    try:
        client.run(full_cwl_path, '{}', [])
    except (ConnectionError, Exception) as e:
        logger.critical(str(e))
        return HttpResponseServerError(e)
    return redirect('scheduler:workflow_list')


def workflow_list(request):
    client = WESClient(service={'auth': settings.WES_AUTH,
                                'proto': settings.WES_PROTO,
                                'host': settings.WES_HOST})
    try:
        service_info = client.get_service_info()
        context = client.list_runs()
    except ConnectionError as e:
        logger.critical(str(e))
        return HttpResponseServerError(e)
    else:
        return render(request, 'scheduler/workflow_list.html', context)


def workflow_detail(request, run_id):
    client = WESClient(service={'auth': settings.WES_AUTH,
                                'proto': settings.WES_PROTO,
                                'host': settings.WES_HOST})
    try:
        run_log = client.get_run_log(run_id)
        context = {'run_log': run_log}
    except ConnectionError as e:
        logger.critical(str(e))
        return HttpResponseServerError(e)
    else:
        return render(request, 'scheduler/workflow_detail.html', context)


def workflow_delete(request, run_id):

    client = WESClient(service={'auth': settings.WES_AUTH,
                                'proto': settings.WES_PROTO,
                                'host': settings.WES_HOST})
    try:
        context = client.get_run_status(run_id)
    except ConnectionError as e:
        logger.critical(str(e))
        return HttpResponseServerError(e)

    if request.method == 'POST':
        logger.info("canceling workflow {}".format(run_id))
        client.cancel(run_id)
        return redirect('scheduler:workflow_list')
    else:
        return render(request, 'scheduler/workflow_confirm_delete.html', context)

