#!/usr/bin/env python

import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

print "\n\n\n\n************************************************************"
print "         If you're installing GradePage, you must also install"
print "               each dependency in requirements.txt"
print "************************************************************\n\n\n\n"

setup(
    name='GradePage',
    version='1.4',
    packages=['course_grader'],
    include_package_data=True,
    install_requires = [
    ],
    dependency_links = [
    ],
    license='Apache License, Version 2.0',  # example license
    description='UW application that support online grade submission',
    long_description=README,
    url='https://github.com/uw-it-aca/gradepage',
    author = "UW-IT ACA",
    author_email = "aca-it@uw.edu",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
