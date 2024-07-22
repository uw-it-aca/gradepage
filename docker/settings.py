from .base_settings import *
from google.oauth2 import service_account
import os

INSTALLED_APPS += [
    'course_grader.apps.CourseGraderConfig',
    'supporttools',
    'userservice',
    'persistent_message',
    'rc_django',
    'grade_conversion_calculator',
    'django.contrib.humanize',
]

MIDDLEWARE += [
    'userservice.user.UserServiceMiddleware',
]

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'supporttools.context_processors.supportools_globals',
    'course_grader.context_processors.persistent_messages',
]

if os.getenv('ENV', 'localdev') == 'localdev':
    DEBUG = True
    GRADEPAGE_SUPPORT_GROUP = 'u_test_group'
    GRADEPAGE_ADMIN_GROUP = 'u_test_group'
    CURRENT_DATETIME_OVERRIDE = '2013-06-17 10:00:00'
    PAST_TERMS_VIEWABLE = 1
    MEDIA_ROOT = os.getenv('IMPORT_DATA_ROOT', '/app/csv')
    VITE_MANIFEST_PATH = os.path.join(
        BASE_DIR, "course_grader", "static", "manifest.json")

else:
    GRADEPAGE_SUPPORT_GROUP = os.getenv('SUPPORT_GROUP', 'u_acadev_gradepage_support')
    GRADEPAGE_ADMIN_GROUP = os.getenv('ADMIN_GROUP', 'u_acadev_gradepage_admins')
    RESTCLIENTS_DAO_CACHE_CLASS = 'course_grader.cache.RestClientsCache'
    PAST_TERMS_VIEWABLE = 4
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.gcloud.GoogleCloudStorage',
            'OPTIONS': {
                'project_id': os.getenv('STORAGE_PROJECT_ID', ''),
                'bucket_name': os.getenv('STORAGE_BUCKET_NAME', ''),
                'location': os.path.join(os.getenv('STORAGE_DATA_ROOT', '')),
                'credentials': service_account.Credentials.from_service_account_file(
                    '/gcs/credentials.json'),
            }
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }
    CSRF_TRUSTED_ORIGINS = ['https://' + os.getenv('CLUSTER_CNAME')]
    VITE_MANIFEST_PATH = os.path.join(os.sep, "static", "manifest.json")

ALLOW_GRADE_SUBMISSION_OVERRIDE = (os.getenv('ENV', 'localdev') != 'prod')
USERSERVICE_VALIDATION_MODULE = 'course_grader.dao.person.is_netid'
USERSERVICE_OVERRIDE_AUTH_MODULE = 'course_grader.views.support.can_override_user'
RESTCLIENTS_ADMIN_AUTH_MODULE = 'course_grader.views.support.can_proxy_restclient'
PERSISTENT_MESSAGE_AUTH_MODULE = 'course_grader.views.support.can_manage_persistent_messages'

EMAIL_NOREPLY_ADDRESS = os.getenv('EMAIL_NOREPLY_ADDRESS')
GRADEPAGE_HOST = 'https://' + os.getenv('CLUSTER_CNAME', 'localhost')
SUBMISSION_DEADLINE_WARNING_HOURS = 41
GRADE_RETENTION_YEARS = 5

GRADEPAGE_SUPPORT_EMAIL = os.getenv('GRADEPAGE_SUPPORT_EMAIL', '')
REGISTRAR_SUPPORT_EMAIL = os.getenv('REGISTRAR_SUPPORT_EMAIL', '')
REGISTRAR_SUPPORT_PHONE = os.getenv('REGISTRAR_SUPPORT_PHONE', '')

COG_FORM_URL = 'https://apps.registrar.washington.edu/grade-change/pages/change.php'

SUPPORTTOOLS_PARENT_APP = 'GradePage'
SUPPORTTOOLS_PARENT_APP_URL = '/'

if os.getenv('AUTH', 'NONE') == 'SAML_MOCK':
    MOCK_SAML_ATTRIBUTES = {
        'uwnetid': ['bill'],
        'affiliations': ['instructor', 'member'],
        'eppn': ['bill@washington.edu'],
        'scopedAffiliations': ['student@washington.edu', 'member@washington.edu'],
        'isMemberOf': ['u_test_group', 'u_test_another_group'],
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'add_user': {
            '()': 'course_grader.log.UserFilter'
        },
        'stdout_stream': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: record.levelno < logging.WARNING
        },
        'stderr_stream': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: record.levelno > logging.INFO
        }
    },
    'formatters': {
        'course_grader': {
            'format': '%(levelname)-4s %(asctime)s %(user)s %(actas)s %(message)s [%(name)s]',
            'datefmt': '[%Y-%m-%d %H:%M:%S]',
        },
        'restclients_timing': {
            'format': '%(levelname)-4s restclients_timing %(module)s %(asctime)s %(message)s [%(name)s]',
            'datefmt': '[%Y-%m-%d %H:%M:%S]',
        },
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'filters': ['add_user', 'stdout_stream'],
            'formatter': 'course_grader',
        },
        'stderr': {
            'class': 'logging.StreamHandler',
            'stream': sys.stderr,
            'filters': ['add_user', 'stderr_stream'],
            'formatter': 'course_grader',
        },
        'restclients_timing': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'filters': ['stdout_stream'],
            'formatter': 'restclients_timing',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['stderr'],
            'level': 'ERROR',
            'propagate': True,
        },
        'course_grader': {
            'handlers': ['stdout', 'stderr'],
            'level': 'INFO',
            'propagate': False,
        },
        'restclients_core': {
            'handlers': ['restclients_timing'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['stdout', 'stderr'],
            'level': 'INFO' if os.getenv('ENV', 'localdev') == 'prod' else 'DEBUG'
        }
    }
}
