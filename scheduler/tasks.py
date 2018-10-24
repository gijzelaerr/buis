import logging
from celery import shared_task
import git
from scheduler.models import Repository

logger = logging.getLogger(__name__)


@shared_task
def checkout(pk, branch='master'):
    logger.info(f"checking out repo for repository {pk}")
    db_repo = Repository.objects.get(pk=pk)
    db_repo.state = db_repo.UPDATING
    db_repo.save()
    try:
        logger.info(f"cloning repository {pk} from {db_repo.url} on branch {branch}")
        disk_repo = db_repo.clone(branch=branch)
    except git.exc.GitCommandError as e:
        logger.error(f"cloning repository {pk} failed: {e}")
        db_repo.state = db_repo.ERROR
        db_repo.save()
    else:
        logger.info("checking out repository {pk} successful")
        db_repo.state = db_repo.READY
        db_repo.save()


@shared_task
def update(pk):
    db_repo = Repository.objects.get(pk=pk)
    db_repo.state = db_repo.UPDATING
    db_repo.save()
    try:
        db_repo.pull()
    except git.exc.GitCommandError as e:
        logger.error(f"cloning repository {pk} failed: {e}")
        db_repo.state = db_repo.ERROR
        db_repo.save()
    else:
        db_repo.state = db_repo.READY
        db_repo.save()