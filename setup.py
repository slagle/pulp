#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2010 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

import os
from setuptools import setup, find_packages

requires = [
    'web.py', 'pymongo', 'simplejson', 'isodate', 'oauth2', 'BeautifulSoup',
    'm2crypto',
]

setup(
    name='pulp',
    version='2.01',
    description='content mangement and delivery',
    author='Pulp Team',
    author_email='pulp-list@redhat.com',
    url='http://pulpproject.org',
    license='GPLv2+',
    packages=find_packages(),
    scripts=[ ],
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: GNU General Puclic License (GPL)',
        'Programming Language :: Python',
        'Operating System :: POSIX',
        'Topic :: Content Management and Delivery',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
    ],
    install_requires=requires,
)

