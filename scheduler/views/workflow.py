import json
from os import path
from urllib.parse import unquote
import logging

from ruamel import yaml

from cwl_utils.parser_v1_0 import load_document
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView, DetailView

from scheduler.models import Repository, Workflow
from scheduler.tasks import run_workflow
from scheduler.util import cwl2dot, CwlForm, list_files

logger = logging.getLogger(__name__)


@login_required
def workflow_visualize(request, repo_id, cwl_path):
    repo = Repository.objects.get(pk=repo_id)
    repo_path = repo.path()
    full_cwl_path = (repo_path / unquote(cwl_path)).resolve()
    assert (full_cwl_path.exists())
    assert (repo_path in full_cwl_path.parents)
    dot, error = cwl2dot(str(full_cwl_path))
    context = {'repo': repo, 'cwl_path': cwl_path, 'dot': dot, 'error': error}
    return render(request, 'scheduler/workflow_visualize.html', context)


@login_required
def workflow_job(request, repo_id, cwl_path):
    repo = Repository.objects.get(pk=repo_id)
    repo_path = repo.path()
    full_cwl_path = (repo_path / unquote(cwl_path)).resolve()
    assert (full_cwl_path.exists())
    assert (repo_path in full_cwl_path.parents)
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
    full_cwl_path = repo_path / unquote(unquote(cwl_path))
    assert (full_cwl_path.exists())
    assert (repo_path in full_cwl_path.parents)

    job = {}
    if 'job' in request.GET:
        job_path = (repo_path / request.GET['job']).resolve()
        assert (job_path.exists())
        assert (repo_path in job_path.parents)
        try:
            with open(job_path) as f:
                job = yaml.load(f)
        except Exception as e:
            logger.error(f"can't parse {job_path}: {e}")

    parsed_workflow = load_document(str(full_cwl_path))
    if request.method == 'POST':
        form = CwlForm(parsed_workflow.inputs, data=request.POST, prefix=repo_path, default_values=job)
        if form.is_valid():
            relative_cwl = full_cwl_path.relative_to(repo_path)
            workflow = Workflow(repository=repo, cwl_path=relative_cwl)
            workflow.save()

            with open(workflow.full_job_path(), mode='wt') as job:
                json.dump(form.back_to_cwl_job(), job)

            run_workflow.delay(pk=workflow.id)

            return redirect('scheduler:workflow_list')

    else:
        form = CwlForm(parsed_workflow.inputs, prefix=repo_path, default_values=job)

    context = {'workflow': parsed_workflow, 'form': form, 'repo': repo, 'cwl_path': cwl_path}
    return render(request, 'scheduler/workflow_parse.html', context)


@login_required
def workflow_restart(_, pk):
    run_workflow.delay(pk=pk)
    return redirect('scheduler:workflow_list')


@login_required
def workflow_run(_, repo_id, cwl_path):
    repo = Repository.objects.get(pk=repo_id)

    full_cwl_path = path.abspath(path.join(repo.path(), unquote(cwl_path)))
    assert (full_cwl_path.startswith(repo.path()))

    workflow = Workflow(repository=repo)
    workflow.save()
    return redirect('scheduler:workflow_list')


class WorkflowCreate(LoginRequiredMixin, CreateView):
    model = Workflow


class WorkflowList(LoginRequiredMixin, ListView):
    model = Workflow

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = 'workflow'
        return context


class WorkflowDelete(LoginRequiredMixin, DeleteView):
    model = Workflow
    success_url = reverse_lazy('scheduler:workflow_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = 'repo'
        return context


class WorkflowDetail(LoginRequiredMixin, DetailView):
    model = Workflow

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = 'repo'
        return context
