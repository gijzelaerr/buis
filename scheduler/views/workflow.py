import json
import logging
from pathlib import Path

from ruamel import yaml

from cwl_utils.parser_v1_0 import load_document
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView, DetailView

from scheduler.models import Repository, Workflow
from scheduler.tasks import run_workflow
from scheduler.util import list_files, parse_job
from scheduler.cwl import CwlForm, cwl2dot

logger = logging.getLogger(__name__)


@login_required
def workflow_visualize(request, repo_id, cwl_path):
    repo = Repository.objects.get(pk=repo_id)
    full_cwl_path = repo.get_content(cwl_path)
    dot, error = cwl2dot(str(full_cwl_path))
    context = {'repo': repo, 'cwl_path': cwl_path, 'dot': dot, 'error': error}
    return render(request, 'scheduler/workflow_visualize.html', context)


@login_required
def workflow_job(request, repo_id, cwl_path):
    """
    Construct a list of job files in the repository and let the user choose one
    """
    repo = Repository.objects.get(pk=repo_id)
    _ = repo.get_content(cwl_path)  # make sure the cwl file exists
    files = list_files(repo.path(), extensions=['yml', 'yaml'])

    jobs = {}
    for file in files:
        try:
            with open(repo.path() / file) as f:
                jobs[file] = yaml.load(f)

        except Exception as e:
            logger.error(f"can't parse {file}: {e}")

    context = {'jobs': jobs, 'repo': repo, 'cwl_path': cwl_path}
    return render(request, 'scheduler/workflow_job.html', context)


@login_required
def workflow_parse(request, repo_id, cwl_path):
    """
    Parses a workflow and optionally a job file. Then gathers all fields from the user.
    """
    repo = Repository.objects.get(pk=repo_id)
    full_cwl_path = repo.get_content(cwl_path)

    job = {}
    if 'job' in request.GET:
        job_path = repo.get_content(request.GET['job'])
        try:
            job = parse_job(Path(job_path), repo.path())
        except Exception as e:
            logger.error(f"can't parse {job_path}: {e}")
            raise

    parsed_workflow = load_document(str(full_cwl_path))

    if request.method == 'POST':
        form = CwlForm(parsed_workflow.inputs, data=request.POST, prefix=repo.path(), default_values=job)
        if form.is_valid():
            relative_cwl = full_cwl_path.relative_to(repo.path())
            workflow = Workflow(repository=repo, cwl_path=relative_cwl)
            workflow.save()

            with open(workflow.full_job_path(), mode='wt') as job:
                json.dump(form.back_to_cwl_job(repo.path()), job)

            run_workflow.delay(pk=workflow.id)

            return redirect('scheduler:workflow_list')

    else:
        form = CwlForm(parsed_workflow.inputs, prefix=repo.path(), default_values=job)

    context = {'workflow': parsed_workflow, 'form': form, 'repo': repo, 'cwl_path': cwl_path}
    return render(request, 'scheduler/workflow_parse.html', context)


@login_required
def workflow_restart(_, pk):
    run_workflow.delay(pk=pk)
    return redirect('scheduler:workflow_list')


@login_required
def workflow_run(_, repo_id, cwl_path):
    repo = Repository.objects.get(pk=repo_id)
    _ = repo.get_content(cwl_path)  # make sure the CWL file exists
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
