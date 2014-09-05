"""
Django settings for organizat project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-s6kxwm3fh0i5wu(2ygr9s*&3mai9b*^+$3ck^v)vq@$3dv60j'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'produccion',
    'planificacion',
    'calendario',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
  "django.contrib.auth.context_processors.auth",
  "django.core.context_processors.request",
  "django.core.context_processors.i18n",
  'django.contrib.messages.context_processors.messages',
)

ROOT_URLCONF = 'organizat.urls'

WSGI_APPLICATION = 'organizat.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
  '/var/www/static/',
  )

GRAPPELLI_ADMIN_TITLE = _('DjProd')
GRAPPELLI_INDEX_DASHBOARD = 'organizat.dashboard.CustomIndexDashboard'

SKIP_SOUTH_TESTS = True # To disable South's own unit tests
SOUTH_TESTS_MIGRATE = False # To disable migrations and use syncdb instead

LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'handlers': {
    'info': {
      'level': 'INFO',
      #'level': 'DEBUG',
      'class': 'logging.FileHandler',
      'filename': 'info.log',
    },
    'debug': {
      #'level': 'INFO',
      'level': 'DEBUG',
      'class': 'logging.FileHandler',
      'filename': 'debug.log',
    },
  },
  'loggers': {
    'planificacion': {
      'handlers': ['info', 'debug'],
      #'level': 'INFO',
      'level': 'DEBUG',
      'propagate': False,
    },
  },
}
