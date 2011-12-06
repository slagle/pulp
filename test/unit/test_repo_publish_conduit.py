#!/usr/bin/python
#
# Copyright (c) 2011 Red Hat, Inc.
#
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

# Python
import datetime
import mock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + "/../common/")
import testutil
import mock_plugins

from pulp.common import dateutils
from pulp.server.content.conduits.repo_publish import RepoPublishConduit, RepoPublishConduitException
from pulp.server.content.plugins.model import Unit, PublishReport
import pulp.server.content.types.database as types_database
import pulp.server.content.types.model as types_model
from pulp.server.db.model.gc_repository import Repo, RepoContentUnit, RepoDistributor
import pulp.server.managers.repo.cud as repo_manager
import pulp.server.managers.repo.distributor as distributor_manager
import pulp.server.managers.repo.publish as publish_manager
import pulp.server.managers.repo.unit_association as association_manager
import pulp.server.managers.content.cud as content_manager
import pulp.server.managers.content.query as query_manager

# constants --------------------------------------------------------------------

TYPE_1_DEF = types_model.TypeDefinition('type_1', 'Type 1', 'One', ['key-1'], ['search-1'], ['type-2'])
TYPE_2_DEF = types_model.TypeDefinition('type_2', 'Type 2', 'Two', ['key-2a', 'key-2b'], [], ['type-1'])

# -- test cases ---------------------------------------------------------------

class RepoSyncConduitTests(testutil.PulpTest):

    def clean(self):
        super(RepoSyncConduitTests, self).clean()
        types_database.clean()

        RepoContentUnit.get_collection().remove()
        Repo.get_collection().remove()

    def setUp(self):
        super(RepoSyncConduitTests, self).setUp()
        mock_plugins.install()
        types_database.update_database([TYPE_1_DEF, TYPE_2_DEF])

        self.repo_manager = repo_manager.RepoManager()
        self.distributor_manager = distributor_manager.RepoDistributorManager()
        self.publish_manager = publish_manager.RepoPublishManager()
        self.association_manager = association_manager.RepoUnitAssociationManager()
        self.content_manager = content_manager.ContentManager()
        self.query_manager = query_manager.ContentQueryManager()

        # Populate the database with a repo with units
        self.repo_manager.create_repo('repo-1')
        self.distributor_manager.add_distributor('repo-1', 'mock-distributor', {}, True, distributor_id='dist-1')

        self.conduit = self._conduit('repo-1', 'dist-1')

        for i in range(0, 100):
            unit_id = 'unit_%d' % i
            self.content_manager.add_content_unit(TYPE_1_DEF.id, unit_id, {'key-1' : 'value_%d' % i})
            self.association_manager.associate_unit_by_id('repo-1', TYPE_1_DEF.id, unit_id)

    def test_str(self):
        """
        Makes sure the __str__ implementation doesn't crash.
        """
        str(self.conduit)

    def test_get_units(self):
        """
        Ensures all the units are returned and in the correct transfer object.
        """

        # Test
        units = self.conduit.get_units()

        # Verify
        self.assertEqual(100, len(units))
        self.assertTrue(isinstance(units[0], Unit)) # make sure its the transfer object
        self.assertEqual(units[0].id, 'unit_0') # spot check
        self.assertEqual(units[0].unit_key['key-1'], 'value_0')

    def test_get_units_no_units(self):
        """
        Makes sure nothing weird happens when there are no associated units.
        """

        # Setup
        for i in range(0, 100):
            self.association_manager.unassociate_unit_by_id('repo-1', TYPE_1_DEF.id, 'unit_%d' % i)

        # Test
        units = self.conduit.get_units()

        # Verify
        self.assertEqual(0, len(units))

    def test_last_publish(self):
        """
        Tests retrieving the last publish time in both the unpublish and previously published cases.
        """

        # Test - Unpublished
        unpublished = self.conduit.last_publish()
        self.assertTrue(unpublished is None)

        # Setup - Previous publish
        last_publish = datetime.datetime.now()
        repo_dist = RepoDistributor.get_collection().find_one({'repo_id' : 'repo-1'})
        repo_dist['last_publish'] = dateutils.format_iso8601_datetime(last_publish)
        RepoDistributor.get_collection().save(repo_dist, safe=True)

        # Test - Last publish
        found = self.conduit.last_publish()
        self.assertTrue(isinstance(found, datetime.datetime)) # check returned format
        self.assertEqual(repo_dist['last_publish'], dateutils.format_iso8601_datetime(found))

    def test_get_set_scratchpad(self):
        """
        Tests scratchpad calls.
        """

        # Test - get no scratchpad
        self.assertTrue(self.conduit.get_scratchpad() is None)

        # Test - set scrathpad
        value = 'dragon'
        self.conduit.set_scratchpad(value)

        # Test - get updated value
        self.assertEqual(value, self.conduit.get_scratchpad())

    def test_build_report(self):
        """
        Tests the conduit utility method for putting together the publish report.
        """

        # Test
        report = self.conduit.build_report('summary', 'details')

        # Verify
        self.assertTrue(isinstance(report, PublishReport))
        self.assertEqual(report.summary, 'summary')
        self.assertEqual(report.details, 'details')

    # -- errors tests ---------------------------------------------------------

    def test_get_units_with_error(self):
        # Setup
        self.conduit._RepoPublishConduit__association_manager = mock.Mock()
        self.conduit._RepoPublishConduit__association_manager.get_units.side_effect = Exception()

        # Test
        try:
            self.conduit.get_units()
            self.fail('Exception expected')
        except RepoPublishConduitException, e:
            print(e) # for coverage

    def test_last_publish_with_error(self):
        # Setup
        self.conduit._RepoPublishConduit__repo_publish_manager = mock.Mock()
        self.conduit._RepoPublishConduit__repo_publish_manager.last_publish.side_effect = Exception()

        # Test
        self.assertRaises(RepoPublishConduitException, self.conduit.last_publish)

    def test_scratchpad_with_error(self):
        # Setup
        self.conduit._RepoPublishConduit__repo_distributor_manager = mock.Mock()
        self.conduit._RepoPublishConduit__repo_distributor_manager.get_distributor_scratchpad.side_effect = Exception()
        self.conduit._RepoPublishConduit__repo_distributor_manager.set_distributor_scratchpad.side_effect = Exception()

        # Test
        self.assertRaises(RepoPublishConduitException, self.conduit.get_scratchpad)
        self.assertRaises(RepoPublishConduitException, self.conduit.set_scratchpad, 'foo')

    # -- utilities ------------------------------------------------------------

    def _conduit(self, repo_id, dist_id):
        """
        Convenience method for creating a conduit.
        """
        conduit = RepoPublishConduit(repo_id, dist_id, self.repo_manager, self.distributor_manager,
                                     self.publish_manager, self.association_manager, self.query_manager)
        return conduit