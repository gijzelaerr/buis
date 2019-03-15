from .base import *

import os
DEBUG = True

SECRET_KEY = os.environ['SECRET_KEY']

CELERY_BROKER_URL = 'amqp://broker/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}

TOIL_BIN = '/usr/local/bin/toil-cwl-runner'
CWLTOOL_BIN = '/usr/local/bin/cwltool'


ALLOWED_HOSTS = [
    'happili-01:8000',
    'happili-01',
    'localhost',
    '127.0.0.1',
    'demo.pythonic.nl',
]
