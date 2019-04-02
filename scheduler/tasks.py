import logging
from celery import shared_task
import git
from scheduler.models import Repository, RepositoryStateChange, Workflow
from shutil import rmtree
import subprocess
import re
from sys import prefix
from os import environ
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def checkout(pk: int, branch='master'):
    logger.info(f"checking out repo for repository {pk}")
    db_repo = Repository.objects.get(pk=pk)
    db_repo.set_state(RepositoryStateChange.UPDATING)
    db_repo.save()
    try:
        logger.info(f"cloning repository {pk} from {db_repo.url} on branch {branch}")
        disk_repo = db_repo.clone(branch=branch)
    except git.exc.GitCommandError as e:
        logger.error(f"cloning repository {pk} failed: {e}")
        db_repo.set_state(RepositoryStateChange.ERROR, e)
        db_repo.save()
    else:
        logger.info("checking out repository {pk} successful")
        db_repo.set_state(RepositoryStateChange.READY)
        db_repo.save()


@shared_task
def update(pk: int):
    db_repo = Repository.objects.get(pk=pk)
    db_repo.set_state(RepositoryStateChange.UPDATING)
    db_repo.save()
    try:
        logger.info(f"updating repository {pk}")
        db_repo.pull()
    except git.exc.GitCommandError as e:
        logger.error(f"cloning repository {pk} failed: {e}")
        db_repo.set_state(RepositoryStateChange.ERROR, e)
        db_repo.save()
    else:
        logger.info(f"finished updating repository {pk}")
        db_repo.set_state(RepositoryStateChange.READY)
        db_repo.save()


def insert_newliners(s):
    return re.sub("(.{120})", "\\1\n", s, 0, re.DOTALL)


@shared_task
def run_workflow(pk: int):
    logger.info(f"Starting workflow {pk}")
    workflow = Workflow.objects.get(pk=pk)
    workflow.state = workflow.RUNNING
    workflow.error_message = ""
    workflow.save()

    stdout_file = str(workflow.path() / "stdout")
    stderr_file = str(workflow.path() / "stderr")
    workdir = workflow.workdir()
    workdir.mkdir(parents=True, exist_ok=True)

    jobstore = workflow.jobstore()
    if jobstore.exists():
        rmtree(str(jobstore))

    path = f"{environ['PATH']}:{prefix}/bin"

    with open(stdout_file, mode='wt') as stdout:
        with open(stderr_file, mode='wt') as stderr:
            args = [
                settings.TOIL_BIN,
                '--jobStore', str(jobstore),
                '--workDir', str(workdir),
                '--stats',
                str(workflow.full_cwl_path()),
                str(workflow.full_job_path())]
            try:
                subprocess.run(args, check=True, stdout=stdout, stderr=stderr, env={'PATH': path})
            except Exception as e:
                logger.error(e)
                workflow.error_message = insert_newliners(str(e))
                workflow.state = workflow.ERROR
                workflow.save()
            else:
                workflow.state = workflow.DONE
                workflow.save()
