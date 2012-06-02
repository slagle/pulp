# -*- coding: utf-8 -*-

# Copyright © 2010-2011 Red Hat, Inc.
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
from gettext import gettext as _

from pulp.server.db.model import Repo

_log = logging.getLogger('pulp')

version = 13

def _migrate_repos():
    collection = Repo.get_collection()
    for repo in collection.find({}):
        if repo['source'] and repo['source']['type'] == u'yum':
            _log.info(_('updating url source type for repo %s') % repo['id'])
            repo['source']['type'] = u'remote'
            collection.save(repo, safe=True)

def migrate():
    # There's a bit of the chicken and the egg problem here, since versioning
    # wasn't built into pulp from the beginning, we just have to bite the
    # bullet and call some initial state of the data model 'version 1'.
    # So this function is essentially a no-op.
    _log.info('migration to data model version %d started' % version)
    _migrate_repos()
    _log.info('migration to data model version %d complete' % version)
