from .base import *


import os

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['demo.pythonic.nl']


DEBUG = False