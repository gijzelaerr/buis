from logging import getLogger
from os import listdir, path, walk
from django.views.generic import ListView, DetailView, DeleteView
from .models import Repository, RepositoryStateChange, Workflow
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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from cwl_utils.parser_v1_0 import load_document
from scheduler.util import CwlForm
from urllib.parse import unquote
import yaml
import pathlib

logger = getLogger(__name__)


def list_files(prefix: pathlib.Path, extensions=None):
    if not extensions:
        extensions = ['cwl']
    for root, dirs, files in walk(str(prefix)):
        subfolder = root[len(str(prefix))+1:]
        for f in files:
            if f.split('.')[-1] in extensions:
                yield path.join(subfolder, f)


class RepositoryDelete(LoginRequiredMixin, DeleteView):
    model = Repository
    success_url = reverse_lazy('scheduler:repo_list')


class RepositoryListCreate(LoginRequiredMixin, ListCreateAPIView):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer


class RepositoryIndex(LoginRequiredMixin, ListView):
    model = Repository


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
def repository_update(request, pk):
    repo = Repository.objects.get(pk=pk)
    repo.set_state(RepositoryStateChange.OUTDATED)
    repo.save()
    update.delay(pk=pk)
    return redirect('scheduler:repo_list')


@login_required
def workflow_job(request, repo_id, cwl_path):
    repo = Repository.objects.get(pk=repo_id)
    repo_path = repo.path()
    full_cwl_path = (repo_path / unquote(cwl_path)).resolve()
    assert(full_cwl_path.exists())
    assert(repo_path in full_cwl_path.parents)
    files = list_files(repo.path(), extensions=['yml', 'yaml'])

    jobs = {}
    for file in files:
        try:
            with open(repo_path / file) as f:
                jobs[file] = yaml.load(f)
        except Exception as e:
            logger.error(f"can't parse {file}: {e}")

    context = {'jobs': jobs, 'repo': repo, 'cwl_path': cwl_path}
    return render(request, 'scheduler/workflow_job.html', context)


@login_required
def workflow_parse(request, repo_id, cwl_path):
    repo = Repository.objects.get(pk=repo_id)
    repo_path = repo.path()
    full_cwl_path = repo_path / unquote(cwl_path)
    assert(full_cwl_path.exists())
    assert(repo_path in full_cwl_path.parents)

    job = {}
    if 'job' in request.GET:
        job_path = (repo_path / request.GET['job']).resolve()
        assert(job_path.exists())
        assert(repo_path in job_path.parents)
        try:
            with open(job_path) as f:
                job = yaml.load(f)
        except Exception as e:
            logger.error(f"can't parse {job_path}: {e}")

    workflow = load_document(str(full_cwl_path))
    form = CwlForm(workflow.inputs, prefix=repo_path, values=job)
    context = {'workflow': workflow, 'form': form}
    return render(request, 'scheduler/workflow_parse.html', context)


@login_required()
def workflow_stage(request, repo_id, cwl_path):
    repo = Repository.objects.get(pk=repo_id)
    repo_path = repo.path()
    full_cwl_path = repo_path / unquote(cwl_path)
    assert(full_cwl_path.exists())
    assert(repo_path in full_cwl_path.parents)


@login_required
def workflow_run(request, repo_id, cwl_path):
    client = WESClient(service={'auth': settings.WES_AUTH,
                                'proto': settings.WES_PROTO,
                                'host': settings.WES_HOST})

    repo = Repository.objects.get(pk=repo_id)

    full_cwl_path = path.abspath(path.join(repo.path(), unquote(cwl_path)))
    assert(full_cwl_path.startswith(repo.path()))
    try:
        response = client.run(full_cwl_path, '{}', [])
    except (ConnectionError, Exception) as e:
        logger.critical(str(e))
        return HttpResponseServerError(e)
    workflow = Workflow(repository=repo, run_id=response['run_id'])
    workflow.save()
    return redirect('scheduler:workflow_list')


@login_required
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


@login_required
def workflow_detail(request, run_id):
    client = WESClient(service={'auth': settings.WES_AUTH,
                                'proto': settings.WES_PROTO,
                                'host': settings.WES_HOST})
    try:
        context = client.get_run_log(run_id)
    except ConnectionError as e:
        logger.critical(str(e))
        return HttpResponseServerError(e)
    else:
        return render(request, 'scheduler/workflow_detail.html', context)


@login_required
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

