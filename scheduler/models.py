from django.db import models
from django.urls import reverse
from django.conf import settings
from os import path
import git


class Repository(models.Model):
    url = models.CharField(max_length=2083)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('scheduler:detail', args=[str(self.id)])

    def __str__(self):
        return self.url

    def path(self):
        return path.join(settings.GIT_DIR, str(self.pk))

    def _get_disk_repo(self):
        return git.Repo(self.path())

    def active_branch(self):
        return self._get_disk_repo().active_branch

    def branches(self):
        return self._get_disk_repo().branches

    def refs(self):
        return self._get_disk_repo().refs

    def pull(self):
        return self._get_disk_repo().remotes.origin.pull()

    def clone(self, branch='master'):
        return git.Repo.clone_from(self.url,
                                   path.join(settings.GIT_DIR, str(self.pk)),
                                   branch=branch)

    def get_state(self):
        return RepositoryStateChange.objects.filter(repository_id=self).first()

    def set_state(self, state, message=None):
        rsc = RepositoryStateChange(repository=self, state=state, message=message)
        rsc.save()
        return rsc


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
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='workflows')
    run_id = models.CharField(max_length=32)
