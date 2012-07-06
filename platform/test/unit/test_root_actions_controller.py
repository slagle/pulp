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

import base

from pulp.server.managers.auth.user import UserManager
import pulp.server.auth.cert_generator as cert_generator
from pulp.server.auth.certificate import Certificate

class UserCertificateControllerTests(base.PulpWebserviceTests):

    def test_get(self):
        # Setup

        user_manager = UserManager()
        user = user_manager.find_by_login(login='ws-user')

        # Test
        status, body = self.post('/v2/actions/login/')

        # Verify
        self.assertEqual(200, status)

        certificate = Certificate(content=str(body))
        cn = certificate.subject()['CN']
        username, id = cert_generator.decode_admin_user(cn)

        self.assertEqual(username, user['login'])
        self.assertEqual(id, user['id'])
