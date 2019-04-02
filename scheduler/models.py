from django.db import models
from django.urls import reverse
from django.conf import settings
import pathlib
import git
from scheduler.util import toil_jobstore_info


class Repository(models.Model):
    url = models.CharField(max_length=2083)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('scheduler:detail', args=[str(self.id)])

    def __str__(self):
        return self.url

    def path(self):
        return pathlib.Path(settings.REPO_DIR) / str(self.pk)

    def _get_disk_repo(self):
        return git.Repo(str(self.path()))

    def active_branch(self):
        return self._get_disk_repo().active_branch

    def branches(self):
        return self._get_disk_repo().branches

    def refs(self):
        return self._get_disk_repo().refs

    def pull(self):
        return self._get_disk_repo().remotes.origin.pull()

    def clone(self, branch='master'):
        return git.Repo.clone_from(self.url, str(self.path()), branch=branch)

    def get_state(self):
        return RepositoryStateChange.objects.filter(repository_id=self).last()

    def set_state(self, state, message=None):
        rsc = RepositoryStateChange(repository=self, state=state, message=message)
        rsc.save()
        return rsc

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.path().mkdir(parents=True, exist_ok=True)


class RepositoryStateChange(models.Model):
    READY = 'RE'
    OUTDATED = 'OU'
    UPDATING = 'UP'
    ADDED = 'AD'
    ERROR = 'ER'

    STATE_CHOICES = (
        (READY, 'Ready'),
        (OUTDATED, 'Outdated'),
        (UPDATING, 'Updating'),
        (ADDED, 'Added'),
        (ERROR, 'Error'),
    )

    ordering = ['-moment']

    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='state_changes')
    message = models.TextField(null=True)
    moment = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default=ADDED)

    def __str__(self):
        return self.get_state_display()


class Workflow(models.Model):
    ADDED = 'AD'
    RUNNING = 'RU'
    ERROR = 'ER'
    DONE = 'OK'

    STATE_CHOICES = (
        (ADDED, 'Added'),
        (RUNNING, 'Running'),
        (ERROR, 'Error'),
        (DONE, 'Done'),
    )

    ordering = ['-moment']

    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='workflows')
    moment = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default=ADDED)
    cwl_path = models.CharField(max_length=100)
    error_message = models.TextField(blank=True)

    def path(self):
        return pathlib.Path(settings.WORKFLOW_DIR) / str(self.pk)

    def full_cwl_path(self):
        return self.repository.path() / self.cwl_path

    def full_job_path(self):
        return self.path() / "job.json"

    def workdir(self):
        return self.path() / 'work'

    def jobstore(self):
        return self.path() / 'job'

    def outdir(self):
        return self.path() / 'outdir'

    def toil_status(self):
        return toil_jobstore_info(str(self.jobstore()))

    def results(self):
        outdir = self.outdir()
        if outdir.exists():
            return outdir.iterdir()
        else:
            return []

    def get_result(self, file_):
        fullpath = (self.outdir() / file_).resolve()
        assert (fullpath.exists())
        assert (self.outdir() in fullpath.parents)
        return fullpath

    def stdout(self):
        try:
            return open(self.path() / "stdout").read()
        except FileNotFoundError:
            return ""

    def stderr(self):
        try:
            return open(self.path() / "stderr").read()
        except FileNotFoundError:
            return ""

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.path().mkdir(parents=True, exist_ok=True)
