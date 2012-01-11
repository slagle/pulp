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

from gettext import gettext as _
import logging
import sys

import pulp.server.managers.factory as manager_factory

# -- constants ----------------------------------------------------------------

_LOG = logging.getLogger(__name__)

# -- importer -----------------------------------------------------------------

class ImporterConduitException(Exception):
    """
    General exception that wraps any exception coming out of the Pulp server.
    """
    pass

class BaseImporterConduit:

    def __init__(self, repo_id, importer_id):
        self.repo_id = repo_id
        self.importer_id = importer_id

    def get_scratchpad(self):
        """
        Returns the value set in the scratchpad for this repository. If no
        value has been set, None is returned.

        @return: value saved for the repository and this importer
        @rtype:  <serializable>

        @raises ImporterConduitException: wraps any exception that may occur
                in the Pulp server
        """

        try:
            importer_manager = manager_factory.repo_importer_manager()
            value = importer_manager.get_importer_scratchpad(self.repo_id)
            return value
        except Exception, e:
            _LOG.exception(_('Error getting scratchpad for repo [%s]' % self.repo_id))
            raise ImporterConduitException(e), None, sys.exc_info()[2]

    def set_scratchpad(self, value):
        """
        Saves the given value to the scratchpad for this repository. It can later
        be retrieved in subsequent syncs through get_scratchpad. The type for
        the given value is anything that can be stored in the database (string,
        list, dict, etc.).

        @param value: will overwrite the existing scratchpad
        @type  value: <serializable>

        @raises ImporterConduitException: wraps any exception that may occur
                in the Pulp server
        """
        try:
            importer_manager = manager_factory.repo_importer_manager()
            importer_manager.set_importer_scratchpad(self.repo_id, value)
        except Exception, e:
            _LOG.exception(_('Error setting scratchpad for repo [%s]' % self.repo_id))
            raise ImporterConduitException(e), None, sys.exc_info()[2]

# -- distributor --------------------------------------------------------------

class DistributorConduitException(Exception):
    """
    General exception that wraps any exception coming out of the Pulp server.
    """
    pass

class BaseDistributorConduit:

    def __init__(self, repo_id, distributor_id):
        self.repo_id = repo_id
        self.distributor_id = distributor_id

    def get_scratchpad(self):
        """
        Returns the value set in the scratchpad for this repository. If no
        value has been set, None is returned.

        @return: value saved for the repository and this distributor
        @rtype:  <serializable>

        @raises DistributorConduitException: wraps any exception that may occur
                in the Pulp server
        """
        try:
            distributor_manager = manager_factory.repo_distributor_manager()
            value = distributor_manager.get_distributor_scratchpad(self.repo_id, self.distributor_id)
            return value
        except Exception, e:
            _LOG.exception('Error getting scratchpad for repository [%s]' % self.repo_id)
            raise DistributorConduitException(e), None, sys.exc_info()[2]

    def set_scratchpad(self, value):
        """
        Saves the given value to the scratchpad for this repository. It can later
        be retrieved in subsequent syncs through get_scratchpad. The type for
        the given value is anything that can be stored in the database (string,
        list, dict, etc.).

        @param value: will overwrite the existing scratchpad
        @type  value: <serializable>

        @raises DistributorConduitException: wraps any exception that may occur
                in the Pulp server
        """
        try:
            distributor_manager = manager_factory.repo_distributor_manager()
            distributor_manager.set_distributor_scratchpad(self.repo_id, self.distributor_id, value)
        except Exception, e:
            _LOG.exception('Error setting scratchpad for repository [%s]' % self.repo_id)
            raise DistributorConduitException(e), None, sys.exc_info()[2]