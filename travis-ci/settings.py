import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

DEBUG = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'compressor',
    'django_user_agents',
    'supporttools',
    'userservice',
    'rc_django',
    'grade_conversion_calculator',
    'course_grader.apps.CourseGraderConfig',
)

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.PersistentRemoteUserMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
)

ROOT_URLCONF = 'travis-ci.urls'

WSGI_APPLICATION = 'travis-ci.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'add_user': {
            '()': 'course_grader.log.UserFilter'
        },
    },
    'formatters': {
        'course_grader': {
            'format': '%(asctime)s %(user)s %(actas)s %(message)s',
            'datefmt': '[%Y-%m-%d %H:%M:%S]',
        },
    },
    'handlers': {
        'course_grader': {
            'class': 'logging.StreamHandler',
            'filters': ['add_user'],
            'formatter': 'course_grader',
        },
    },
    'loggers': {
        'course_grader': {
            'handlers': ['course_grader'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

GRADEPAGE_ADMIN_GROUP = ''
