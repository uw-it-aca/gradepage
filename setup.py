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
        'Django==2.1.1',
        'django-compressor',
        'django-user-agents',
        'django-userservice>=3.1.2',
        'UW-RestClients-Core>=1.0.2,<2.0',
        'UW-RestClients-SWS>=2.0.3,<3.0',
        'UW-RestClients-PWS>=2.0.2,<3.0',
        'UW-RestClients-GWS>=2.0.1,<3.0',
        'UW-RestClients-Canvas>=1.0.1,<2.0',
        'UW-RestClients-Catalyst>=1.0,<2.0',
        'UW-RestClients-Django-Utils>=2.1.2,<3.0',
        'UW-RestClients-Graderoster>=1.0,<2.0',
        'UW-Grade-Conversion-Calculator>=1.1,<2.0',
        'Django-Safe-EmailBackend>=1.0,<2.0',
        'Django-SupportTools>=3.3,<4.0',
        'Django-Persistent-Message>=0.1.6',
        'UW-Django-SAML2>=1.2.1,<2.0',
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
        'Programming Language :: Python :: 3.6',
    ],
)
