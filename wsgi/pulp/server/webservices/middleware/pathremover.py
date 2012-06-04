# -*- coding: utf-8 -*-
#
# Copyright © 2012 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

import logging

try:
    import json
except ImportError:
    import simplejson as json

from pulp.server.exceptions import OperationPostponed
from pulp.server.webservices.http import http_responses
from pulp.server.webservices import serialization


_LOG = logging.getLogger(__name__)


class PathRemoverMiddleware(object):
    """
    Strip off /pulp/api from the front of the request URI.
    """

    def __init__(self, app):
        self.app = app
        self.headers = {'Content-Encoding': 'utf-8',
                        'Content-Type': 'application/json',
                        'Content-Length': '-1'}

    def __call__(self, environ, start_response):
        path_info = environ["PATH_INFO"]
        f = open("/var/lib/stickshift/06c2ef10f5234e6cb04c3e4c2fe6d3ef/pulp/tmp/log.txt", 'w')
        if path_info.startswith("/pulp/api"):
            environ["PATH_INFO"] = path_info.strip("/pulp/api")
            f.write("here0")
            f.write(str(environ["PATH_INFO"]))
        f.close()
        return self.app(environ, start_response)
