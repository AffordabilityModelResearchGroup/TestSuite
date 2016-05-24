"""
Django settings for affordability_model project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '29p7f51ugehi4=w%(xrw6hldg@#m38zh-uh=z*(3tk^8tx@yto'

# SECURITY WARNING: don't run with debug turned on nin production!
debug = os.environ.get('DEBUG', 'True')
DEBUG = False if debug.lower() == 'false' else True

production = os.environ.get('PRODUCTION', 'False')
PRODUCTION = True if production.lower() == 'true' else False

ALLOWED_HOSTS = ['abilitymodel.herokuapp.com']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Affordability Model App
    'proto1',
    'v2',
    'ipeds',
    # other apps
    'import_export',
    'constance',
    'constance.backends.database',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.gzip.GZipMiddleware'
)

AUTHENTICATION_BACKENDS = ['affordability_model.google_auth.GoogleAuthBackend']

ROOT_URLCONF = 'affordability_model.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'constance.context_processors.config'
            ],
        },
    },
]

WSGI_APPLICATION = 'affordability_model.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {},
    'postgres': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'PASSWORD': 'Saeg2Aijoodah1hing7k',
        'PORT': '5432',
        'USER': 'serveruser',
        'NAME': 'affordability_model'
    },
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {},
    'prod': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'affordability_model_cache',
    },
    'dev': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/staticfiles/'
STATIC_ROOT = 'staticfiles'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)


GOOGLE_CLIENT_ID = '636049794846-1rhbc4errn6vk69qhp5d04ff2jolf013.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'Ww6nChO_O5TCwqN4mnlQ85w9'
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/userinfo.email',
                 'https://www.googleapis.com/auth/userinfo.profile']
GOOGLE_APPS_DOMAIN_NAME = ['uw.edu', 'gmail.com']
LOGIN_URL = '/accounts/google/login'

CACHE_LENGTH = 300  # seconds
if PRODUCTION:
    DATABASES['default'] = DATABASES['postgres']
    CACHES['default'] = CACHES['prod']
else:
    DATABASES['default'] = DATABASES['sqlite']
    MIDDLEWARE_CLASSES += ('yet_another_django_profiler.middleware.ProfilerMiddleware',)
    CACHES['default'] = CACHES['dev']

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG = {
    'TIME_TO_GRADUATE': (4.34, 'Time to graduate value used in the UI'),
    'ENABLE_PLOT_SMOOTH_SWITCH': (False, "Display a switch to toggle smoothing of plots"),
    'DEFAULT_REPAYMENT_TO_INCOME_RATIO': (10,
                                          'Acceptable payment to income ratio for Affordable Debt plot'),
    'DEFAULT_REPAYMENT_YEARS': (10, 'Loan repayment time in years for Affordable Debt plot'),
    'DEFAULT_REPAYMENT_INTEREST': (5, 'Interest rate of student loans for Affordable Debt plot'),

    'DEFAULT_ANNUAL_EARNING_EXCLUSION_LEVEL': (2500, 'Annual earnings exclusion level for this analysis, A0,'
                                                     'expressed in $, typically $2500 - $35000'),
    'DEFAULT_ANNUAL_EARNING_LEVEL_FOR_ANALYSIS': (30, 'Annual earning level for the analysis, A1,'
                                                      'expressed as a percentile of earners above the exclusion level'
                                                      '(typ 0 to 0.5)'),

    'COMMUNITY_COLLEGE_PRO_RATION': (0.4, 'Savings pro-ration for community colleges.'),
    'INSTITUTIONAL_AID_ALWAYS_USE_WEIGHTED_AVG': (True, """if NOT Checked and SNG shown, SNG_Y < 70% and SNG_N > 70%
                                                          if NOT Checked and SNG hidden, SNG_N for 0% -> 200%
                                                          if Checked, Weighted Average"""),
    'SHOW_PERCENTILE_OF_EXCLUDED_EARNER': (True, ''),
    'MAX_ALLOWED_EARNINGS': (100000, """The maximum that any percentile earner is allowed to earn.
    If the percentile earner earns more than the chosen value the system will cap their earnings below this threshold"""),

    'MIN_TIME_TO_GRADUATE': (1.0,
                             "The minimum value that time to graduate accepts, if any value below this number is entered the system bumps it up ")

}

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

ALLOWED_YEARS = range(2007, 2016)

TEST_RUNNER = 'proto1.tests.UseExistingDBDiscoverRunner'

if 'test' in sys.argv:
    del DATABASES['sqlite']
    del DATABASES['postgres']