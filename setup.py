#!/usr/bin/env python

import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/gradepage>`_.
"""

# The VERSION file is created by travis-ci, based on the tag name
version_path = 'course_grader/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='GradePage',
    version=VERSION,
    packages=['course_grader'],
    include_package_data=True,
    install_requires = [
        'Django==1.10.5',
        'django-compressor',
        'django-templatetag-handlebars',
        'nameparser>=0.2.9',
        'django-userservice==1.2.1',
        'AuthZ-Group>=1.6',
        'UW-RestClients-SWS>=1.0,<2.0',
        'UW-RestClients-PWS>=0.5,<1.0',
        'UW-RestClients-GWS>=0.1,<1.0',
        'UW-RestClients-Canvas>=0.2,<1.0',
        'UW-RestClients-Catalyst>=0.1,<1.0',
        'UW-RestClients-Django-Utils>=0.6,<1.0',
        'UW-RestClients-Graderoster>=0.3,<1.0',
        'UW-Grade-Conversion-Calculator>=0.2,<1.0',
        'Django-Safe-EmailBackend>=0.1,<1.0',
        'Django-SupportTools>=1.1',
        'django_mobileesp',
    ],
    license='Apache License, Version 2.0',
    description='UW application that support online grade submission',
    long_description=README,
    url='https://github.com/uw-it-aca/gradepage',
    author = "UW-IT AXDD",
    author_email = "aca-it@uw.edu",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
