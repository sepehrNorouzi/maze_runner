import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_NAME = os.environ.get("PROJECT_NAME", 'maze_runner')

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get("DEBUG", "False") in ['true', 'True', '1']

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(',')

THIRD_PARTY_APPS = [
    'djoser',
    'rest_framework',
    'rest_framework_simplejwt'
]

IN_HOUSE_APP = [
    'common.apps.CommonConfig',
    'maze.apps.MazeConfig',

]

INSTALLED_APPS = [
    'user.apps.UserConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
] + THIRD_PARTY_APPS + IN_HOUSE_APP

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'maze_runner.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['./templates'],
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

WSGI_APPLICATION = 'maze_runner.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': int(os.getenv('POSTGRES_PORT')),
        'CONN_MAX_AGE': int(os.getenv('CONN_MAX_AGE')),
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': "rest_framework.pagination.PageNumberPagination",
    'PAGE_SIZE': int(os.getenv('DEFAULT_PAGE_SIZE', default=20)),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.environ.get("ACCESS_TOKEN_LIFETIME", "5"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.environ.get("REFRESH_TOKEN_LIFETIME", "1"))),
    "AUTH_HEADER_TYPES": ("Bearer",),
}


AUTH_USER_MODEL = 'user.User'

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get('REDIS_URI', ""),
        "TIMEOUT": int(os.getenv('REDIS_TIMEOUT', default='3600')),
        "KEY_PREFIX": os.getenv('REDIS_KEY_PREFIX', default=PROJECT_NAME),
    }
}


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
]

USE_CELERY = os.environ.get("USE_CELERY", "0").lower() in ['1', 'true', 't']

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

STATIC_ROOT = os.environ.get("STATIC_ROOT", 'static')

MEDIA_ROOT = os.environ.get("MEDIA_ROOT", 'uploads')
MEDIA_URL = os.environ.get("MEDIA_URL", "media/")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_HEADER = "{project_name} admin panel".format(project_name=PROJECT_NAME.replace('_', ' ').title())
SITE_TITLE = "Welcome to {project_name} admin panel".format(project_name=PROJECT_NAME.replace('_', ' ').title())


CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULTS_BACKEND")
