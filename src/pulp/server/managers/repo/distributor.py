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

from gettext import gettext as _
import logging
import re
import sys
import uuid

from pulp.server.db.model.gc_repository import Repo, RepoDistributor
import pulp.server.content.loader as plugin_loader
from pulp.server.content.plugins.config import PluginCallConfiguration
import pulp.server.managers.repo._common as common_utils
from pulp.server.managers.repo._common import MissingRepo

# -- constants ----------------------------------------------------------------

_DISTRIBUTOR_ID_REGEX = re.compile(r'^[\-_A-Za-z0-9]+$') # letters, numbers, underscore, hyphen

_LOG = logging.getLogger(__name__)

# -- exceptions ---------------------------------------------------------------

class InvalidDistributorId(Exception):
    """
    Indicates a given distributor ID was invalid.
    """
    def __init__(self, invalid_distributor_id):
        Exception.__init__(self)
        self.invalid_distributor_id = invalid_distributor_id

    def __str__(self):
        return _('Invalid distributor ID [%(id)s]' % {'id' : self.invalid_distributor_id})

class InvalidDistributorConfiguration(Exception):
    """
    Indicates a distributor configuration was specified (either at add_distributor
    time or later updated) but the distributor plugin indicated it was invalid.
    """
    pass

class MissingDistributor(Exception):
    """
    Indicates a distributor was requested that does not exist.
    """
    def __init__(self, distributor_name):
        Exception.__init__(self)
        self.distributor_name = distributor_name

    def __str__(self):
        return _('No distributor with name [%(name)s]' % {'name' : self.distributor_name})

# -- manager ------------------------------------------------------------------

class RepoDistributorManager:

    def add_distributor(self, repo_id, distributor_type_id, distributor_config,
                        auto_distribute, distributor_id=None):
        """
        Adds an association from the given repository to a distributor. The
        association will be tracked through the distributor_id; each distributor
        on a given repository must have a unique ID. If this is not specified,
        one will be generated. If a distributor already exists on the repo for
        the given ID, the existing one will be removed and replaced with the
        newly configured one.

        @param repo_id: identifies the repo
        @type  repo_id: str

        @param distributor_type_id: identifies the distributor; must correspond
                                    to a distributor loaded at server startup
        @type  distributor_type_id: str

        @param distributor_config: configuration the repo will use with this
                                   distributor; may be None
        @type distributor_config:  dict

        @param auto_distribute: if true, this distributor will be invoked at
                                the end of every sync
        @type  auto_distribute: bool

        @param distributor_id: unique ID to refer to this distributor for this repo
        @type  distributor_id: str

        @return: ID assigned to the distributor (only valid in conjunction with the repo)

        @raises MissingRepo: if the given repo_id does not refer to a valid repo
        @raises MissingDistributor: if the given distributor type ID does not
                                    refer to a valid distributor
        @raises InvalidDistributorId: if the distributor ID is provided and unacceptable
        """

        repo_coll = Repo.get_collection()
        distributor_coll = RepoDistributor.get_collection()

        # Validation
        repo = repo_coll.find_one({'id' : repo_id})
        if repo is None:
            raise MissingRepo(repo_id)

        if not plugin_loader.is_valid_distributor(distributor_type_id):
            raise MissingDistributor(distributor_type_id)

        # Determine the ID for this distributor on this repo; will be
        # unique for all distributors on this repository but not globally
        if distributor_id is None:
            distributor_id = str(uuid.uuid4())
        else:
            # Validate if one was passed in
            if not is_distributor_id_valid(distributor_id):
                raise InvalidDistributorId(distributor_id)

        distributor_instance, plugin_config = plugin_loader.get_distributor_by_id(distributor_type_id)
        try:
            valid_config = distributor_instance.validate_config(repo, distributor_config)
        except Exception:
            _LOG.exception('Exception received from distributor [%s] while validating config' % distributor_type_id)
            raise InvalidDistributorConfiguration()

        if not valid_config:
            raise InvalidDistributorConfiguration()

        # If a distributor already exists at that ID, remove it from the database
        # as it will be replaced in this method
        existing_distributor = distributor_coll.find_one({'repo_id' : repo_id, 'id' : distributor_id})
        if existing_distributor is not None:
            distributor_coll.remove(existing_distributor, safe=True)

        # Database Update
        distributor = RepoDistributor(repo_id, distributor_id, distributor_type_id, distributor_config, auto_distribute)
        distributor_coll.save(distributor, safe=True)

        return distributor_id

    def remove_distributor(self, repo_id, distributor_id):
        """
        Removes a distributor from a repository. If there is no
        distributor with the given ID on the repository, this call has no effect
        and will not raise an error.

        @param repo_id: identifies the repo
        @type  repo_id: str

        @param distributor_id: identifies the distributor to delete
        @type  distributor_id: str

        @raises MissingRepo: if repo_id doesn't correspond to a valid repo
        """

        repo_coll = Repo.get_collection()
        distributor_coll = RepoDistributor.get_collection()

        # Validation
        repo = repo_coll.find_one({'id' : repo_id})
        if repo is None:
            raise MissingRepo(repo_id)

        repo_distributor = distributor_coll.find_one({'repo_id' : repo_id, 'id' : distributor_id})

        # Call the distributor's cleanup method
        distributor_type_id = repo_distributor['distributor_type_id']
        distributor_instance, plugin_config = plugin_loader.get_distributor_by_id(distributor_type_id)

        call_config = PluginCallConfiguration(plugin_config, repo_distributor['config'])

        transfer_repo = common_utils.to_transfer_repo(repo)
        transfer_repo.working_dir = common_utils.distributor_working_dir(distributor_type_id, repo_id)

        distributor_instance.distributor_removed(transfer_repo, call_config)

        # Update the database to reflect the removal
        distributor_coll.remove(repo_distributor, safe=True)

    def update_distributor_config(self, repo_id, distributor_id, distributor_config):
        """
        Attempts to update the saved configuration for the given distributor.
        The distributor will be asked if the new configuration is valid. If not,
        this method will raise an error and the existing configuration will
        remain unchanged.

        @param repo_id: identifies the repo
        @type  repo_id: str

        @param distributor_id: identifies the distributor on the repo
        @type  distributor_id: str

        @param distributor_config: new configuration values to use
        @type  distributor_config: dict
        """

        repo_coll = Repo.get_collection()
        distributor_coll = RepoDistributor.get_collection()

        # Input Validation
        repo = repo_coll.find_one({'id' : repo_id})
        if repo is None:
            raise MissingRepo(repo_id)

        repo_distributor = distributor_coll.find_one({'repo_id' : repo_id, 'id' : distributor_id})
        if repo_distributor is None:
            raise MissingDistributor(None)

        distributor_type_id = repo_distributor['distributor_type_id']
        distributor_instance, plugin_config = plugin_loader.get_distributor_by_id(distributor_type_id)

        # Let the distributor plugin verify the configuration
        call_config = PluginCallConfiguration(plugin_config, distributor_config)
        transfer_repo = common_utils.to_transfer_repo(repo)
        transfer_repo.working_dir = common_utils.distributor_working_dir(distributor_type_id, repo_id)

        try:
            valid_config = distributor_instance.validate_config(transfer_repo, call_config)
        except Exception:
            _LOG.exception('Exception raised from distributor [%s] while validating config for repo [%s]' % (distributor_type_id, repo_id))
            raise InvalidDistributorConfiguration, None, sys.exc_info()[2]

        if not valid_config:
            raise InvalidDistributorConfiguration()

        # If we got this far, the new config is valid, so update the database
        repo_distributor['config'] = distributor_config
        distributor_coll.save(repo_distributor, safe=True)

    def get_distributor_scratchpad(self, repo_id, distributor_id):
        """
        Returns the contents of the distributor's scratchpad for the given repo.
        If there is no such distributor or the scratchpad has not been set, None
        is returned.

        @param repo_id: identifies the repo
        @type  repo_id: str

        @param distributor_id: identifies the distributor on the repo
        @type  distributor_id: str

        @return: value set for the distributor's scratchpad
        @rtype:  anything that can be saved in the database
        """

        distributor_coll = RepoDistributor.get_collection()

        # Validatoin
        repo_distributor = distributor_coll.find_one({'repo_id' : repo_id, 'id' : distributor_id})
        if repo_distributor is None:
            return None

        scratchpad = repo_distributor.get('scratchpad', None)
        return scratchpad

    def set_distributor_scratchpad(self, repo_id, distributor_id, contents):
        """
        Sets the value of the scratchpad for the given repo and saves it to the
        database. If there is a previously saved value it will be replaced.

        If there is no distributor with the given ID on the repo, this call does
        nothing.

        @param repo_id: identifies the repo
        @type  repo_id: str

        @param distributor_id: identifies the distributor on the repo
        @type  distributor_id: str

        @param contents: value to write to the scratchpad field
        @type  contents: anything that can be saved in the database
        """

        distributor_coll = RepoDistributor.get_collection()

        # Validation
        repo_distributor = distributor_coll.find_one({'repo_id' : repo_id, 'id' : distributor_id})
        if repo_distributor is None:
            return

        # Update
        repo_distributor['scratchpad'] = contents
        distributor_coll.save(repo_distributor, safe=True)

# -- functions ----------------------------------------------------------------

def is_distributor_id_valid(distributor_id):
    """
    @return: true if the distributor ID is valid; false otherwise
    @rtype:  bool
    """
    result = _DISTRIBUTOR_ID_REGEX.match(distributor_id) is not None
    return result