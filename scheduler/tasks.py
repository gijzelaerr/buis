import logging
from celery import shared_task
import git
from scheduler.models import Repository, RepositoryStateChange, Workflow
import json
from toil.cwl import cwltoil

logger = logging.getLogger(__name__)


@shared_task
def checkout(pk, branch='master'):
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
def update(pk):
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


@shared_task
def run_workflow(pk: int, cwl_file: str, job_dict: dict):
    logger.info(f"Starting workflow {pk} with CWL file {cwl_file}")
    workflow = Workflow.objects.get(pk=pk)
    workflow.state = workflow.RUNNING

    job_file = str(workflow.path() / "job.json")
    stdout_file = str(workflow.path() / "stdout")
    with open(job_file, mode='wt') as job:
        with open(stdout_file, mode='wt') as stdout:
            json.dump(job_dict, job)
            job.flush()
            args = [cwl_file, job_file]
            cwltoil.main(args=args, stdout=stdout)
