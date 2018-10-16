# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from buis.settings import GIT_DIR


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)

def checkout(repository_id):
    pass