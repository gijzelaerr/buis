from .base import *

SECRET_KEY = 'qz6nbqn9kl2)m4t8@ix^mwe^y&e_^s4=9w6q^mif!vk1!pj7=x'

DEBUG = True


INSTALLED_APPS += [
    'debug_toolbar',
]


MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']


MEDIA_ROOT = path.join(BASE_DIR, 'scratch')
MEDIA_URL = '/media/'