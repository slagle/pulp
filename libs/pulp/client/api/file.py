# -*- coding: utf-8 -*-
#
# Copyright © 2011 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

from pulp.client.api.base import PulpAPI


class FileAPI(PulpAPI):
    """
    Connection class to access file related calls
    """
    
    def file(self, id):
        path = "/content/file/%s/" % str(id)
        return self.server.GET(path)[1]
    
    def delete(self, id):
        path = "/content/file/%s/" % id
        return self.server.DELETE(path)[1]
    
    def orphaned_files(self):
        path = "/orphaned/files/"
        return self.server.GET(path)[1]

