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
        'Django~=3.2',
        'django-compressor',
        'django-user-agents',
        'django-userservice~=3.1',
        'django-storages[google]>=1.10',
        'uw-memcached-clients~=1.0',
        'UW-RestClients-Core~=1.3',
        'UW-RestClients-SWS~=2.3',
        'UW-RestClients-PWS~=2.1',
        'UW-RestClients-Canvas>=1.2.3',
        'UW-RestClients-Graderoster~=1.1',
        'UW-RestClients-Django-Utils~=2.3',
        'UW-Grade-Conversion-Calculator~=1.2',
        'Django-Safe-EmailBackend~=1.0',
        'Django-SupportTools~=3.5',
        'Django-Persistent-Message~=1.1',
        'UW-Django-SAML2~=1.7',
        'chardet~=4.0',
    ],
    license='Apache License, Version 2.0',
    description='UW application that supports online grade submission',
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
        'Programming Language :: Python :: 3.8',
    ],
)
