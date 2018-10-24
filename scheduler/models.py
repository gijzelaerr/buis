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

    def _get_disk_repo(self):
        return git.Repo(path.join(settings.GIT_DIR, str(self.pk)))

    def active_branch(self):
        return self._get_disk_repo().active_branch

    def refs(self):
        return self._get_disk_repo().refs

    def pull(self):
        return self._get_disk_repo().remotes.origin.pull()

    def clone(self, branch='master'):
        return git.Repo.clone_from(self.url,
                                   path.join(settings.GIT_DIR, str(self.pk)),
                                   branch=branch)

    def get_state(self):
        RepositoryStateChange.objects.get(repository=self)

    def set_state(self, state, message=None):
        rsc = RepositoryStateChange(repository=self, state=state, message=message)
        rsc.save()


class RepositoryStateChange(models.Model):
    READY = 'RE'
    UPDATING = 'UP'
    ADDED = 'AD'
    ERROR = 'ER'

    STATE_CHOICES = (
        (READY, 'Ready'),
        (UPDATING, 'Updating'),
        (ADDED, 'Added'),
        (ERROR, 'Error'),
    )

    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    moment = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default=ADDED)
    message = models.TextField()