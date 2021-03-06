from os import path

BASE_DIR = path.dirname((path.dirname(path.dirname(path.abspath(__file__)))))

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'scheduler',
    'django_celery_results',
    'rest_framework',
    'frontend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'buis.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'buis.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(BASE_DIR, 'db/db.sqlite3'),
    }
}

STATIC_ROOT = path.join(BASE_DIR, 'static')

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LOGOUT_REDIRECT_URL = 'scheduler:repo_list'
LOGIN_REDIRECT_URL = 'scheduler:repo_list'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

REPO_DIR = path.join(BASE_DIR, 'scratch/repo/')
WORKFLOW_DIR = path.join(BASE_DIR, 'scratch/workflow/')
DATASET_DIR = path.join(BASE_DIR, 'scratch/datasets/')

CELERY_RESULT_BACKEND = 'django-db'

WES_AUTH = None
WES_PROTO = 'http'
WES_HOST = 'localhost:8080'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}


TOIL_BIN = path.join(BASE_DIR, '.venv/bin/toil-cwl-runner')
CWLTOOL_BIN = path.join(BASE_DIR, '.venv/bin/cwltool')
CWL_CACHE = path.join(BASE_DIR, 'scratch/cache/')

CWL_RUNNER = 'cwltool'  # toil or cwltool
