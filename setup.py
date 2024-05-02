#!/usr/bin/env python

import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/gradepage>`_.
"""

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
        'django~=4.2',
        'django-compressor',
        'django-user-agents',
        'django-userservice~=3.2',
        'django-storages[google]',
        'uw-memcached-clients~=1.0',
        'uw-restclients-core~=1.4',
        'uw-restclients-sws~=2.3',
        'uw-restclients-pws~=2.1',
        'uw-restclients-canvas~=1.2',
        'uw-restclients-graderoster~=1.1',
        'uw-restclients-django-utils~=2.3',
        'uw-grade-conversion-calculator~=1.4',
        'django-safe-emailbackend~=1.2',
        'django-supporttools~=3.6',
        'django-persistent-message~=1.3',
        'uw-django-saml2~=1.8',
        'chardet~=4.0',
        'lxml==4.9.4',
        'xmlsec==1.3.13'
    ],
    license='Apache License, Version 2.0',
    description='UW application that supports online grade submission',
    long_description=README,
    url='https://github.com/uw-it-aca/gradepage',
    author="UW-IT T&LS",
    author_email="aca-it@uw.edu",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
