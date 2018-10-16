from django.db import models


class Repository(models.Model):
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

    url = models.CharField(max_length=2083)

    state = models.CharField(max_length=2, choices=STATE_CHOICES, default=ADDED)
