from .base_settings import *
import os

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    'course_grader.apps.CourseGraderConfig',
    'supporttools',
    'userservice',
    'persistent_message',
    'rc_django',
    'grade_conversion_calculator',
    'django.contrib.humanize',
    'django_user_agents',
    'compressor',
]

MIDDLEWARE += [
    'userservice.user.UserServiceMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'supporttools.context_processors.supportools_globals',
    'course_grader.context_processors.user',
    'course_grader.context_processors.has_less_compiled',
    'course_grader.context_processors.debug_mode',
]

COMPRESS_ROOT = '/static/'

STATICFILES_FINDERS += (
    'compressor.finders.CompressorFinder',
)

COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} {outfile}'),
    ('text/x-sass', 'pyscss {infile} > {outfile}'),
    ('text/x-scss', 'pyscss {infile} > {outfile}'),
)

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter'
]

COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

COMPRESS_OFFLINE = True
COMPRESS_OFFLINE_CONTEXT = {
    'wrapper_template': 'persistent_message/manage_wrapper.html',
}

if os.getenv('ENV', '') == 'localdev':
    DEBUG = True
    GRADEPAGE_SUPPORT_GROUP = 'u_test_group'
    GRADEPAGE_ADMIN_GROUP = 'u_test_group'
    CURRENT_DATETIME_OVERRIDE = '2013-06-17 10:00:00'
    PAST_TERMS_VIEWABLE = 1
else:
    GRADEPAGE_SUPPORT_GROUP = os.getenv('SUPPORT_GROUP', 'u_acadev_gradepage_support')
    GRADEPAGE_ADMIN_GROUP = os.getenv('ADMIN_GROUP', 'u_acadev_gradepage_admins')
    RESTCLIENTS_DAO_CACHE_CLASS = 'course_grader.cache.RestClientsMemcachedCache'
    PAST_TERMS_VIEWABLE = 4

ALLOW_GRADE_SUBMISSION_OVERRIDE = (os.getenv('ENV', '') != 'prod')
USERSERVICE_VALIDATION_MODULE = 'course_grader.dao.person.is_netid'
USERSERVICE_OVERRIDE_AUTH_MODULE = 'course_grader.views.support.can_override_user'
RESTCLIENTS_ADMIN_AUTH_MODULE = 'course_grader.views.support.can_proxy_restclient'
PERSISTENT_MESSAGE_AUTH_MODULE = 'course_grader.views.support.can_manage_persistent_messages'

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_TIMEOUT = 15
EMAIL_NOREPLY_ADDRESS = os.getenv('EMAIL_NOREPLY_ADDRESS')
if os.getenv('ENV', '') == 'prod':
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'saferecipient.EmailBackend'
    SAFE_EMAIL_RECIPIENT = os.getenv('SAFE_EMAIL_RECIPIENT')

GRADEPAGE_HOST = 'https://' + os.getenv('CLUSTER_CNAME', 'localhost')
SUBMISSION_DEADLINE_WARNING_HOURS = 48
GRADE_RETENTION_YEARS = 5

GRADEPAGE_SUPPORT_EMAIL = 'help@uw.edu'
REGISTRAR_SUPPORT_EMAIL = os.getenv('REGISTRAR_SUPPORT_EMAIL', '')
REGISTRAR_SUPPORT_PHONE = os.getenv('REGISTRAR_SUPPORT_EMAIL', '')

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
