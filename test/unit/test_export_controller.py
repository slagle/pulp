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
# Python
import os
import shutil
import sys
import logging
from pulp.server.compat import chain
from pulp.server.exporter.distribution import DistributionExporter
from pulp.server.exporter.errata import ErrataExporter
from pulp.server.exporter.other import OtherExporter
from pulp.server.exporter.package import PackageExporter
from pulp.server.exporter.packagegroup import CompsExporter
from pulp.server.tasking import task

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + "/../common/")
import testutil
import time
from pulp.server.exporter.controller import ExportController, ExporterReport
from pulp.server import async, constants, util
from pulp.server.api import repo_sync
logging.root.setLevel(logging.ERROR)
qpid = logging.getLogger('qpid.messaging')
qpid.setLevel(logging.ERROR)

class TestExportController(testutil.PulpAsyncTest):

    def setUp(self):
        testutil.PulpAsyncTest.setUp(self)
        my_dir = os.path.abspath(os.path.dirname(__file__))
        datadir = my_dir + "/data/repo_for_export/"
        repo_url = "file://%s" % datadir
        repo_1 = self.repo_api.create('test_export_repo', 'some name', \
            'i386', 'file://%s' % repo_url)
        self._perform_sync(repo_1)
        self.found_1 = self.repo_api.repository('test_export_repo')
        tgt_dir = '/tmp/pulp/myexport/'
        if not os.path.exists(tgt_dir):
            os.mkdir(tgt_dir)
        self.ec = ExportController(self.found_1, tgt_dir, generate_iso=True)

    def tearDown(self):
        testutil.PulpAsyncTest.tearDown(self)
        shutil.rmtree("/tmp/pulp/myexport/")

    def test_controller_class_load(self):
        classes = self.ec._load_exporter()
        cls_list = [PackageExporter, CompsExporter, ErrataExporter, OtherExporter, DistributionExporter]
        for cls in cls_list:
            assert(cls in classes)

    def test_perform_export(self):
        self.ec.perform_export()
        print self.ec.progress
        # rpms
        self.assertEquals(len(self.found_1['packages']), self.ec.progress['details']['rpm']['num_success'])
        self.assertEquals(0, self.ec.progress['details']['rpm']['items_left'])
        # errata
        repo_errata = list(chain.from_iterable(self.found_1['errata'].values()))
        self.assertEquals(len(repo_errata), self.ec.progress['details']['errata']['num_success'])
        self.assertEquals(0, self.ec.progress['details']['errata']['items_left'])
        # distribution
        distro_files = self.distribution_api.distribution(self.found_1['distributionid'][0])['files']
        self.assertEquals(len(distro_files), self.ec.progress['details']['distribution']['num_success'])
        self.assertEquals(0, self.ec.progress['details']['distribution']['items_left'])
        # package groups + categories
        self.assertEquals(len(self.found_1['packagegroups']) + len(self.found_1['packagegroupcategories']),
               self.ec.progress['details']['packagegroup']['num_success'])
        self.assertEquals(0, self.ec.progress['details']['packagegroup']['items_left'])

        # custom metadata
        tgt_dir = '/tmp/pulp/myexport/'
        repomd_path = os.path.join(tgt_dir, 'repodata/repomd.xml')
        
        assert(os.path.exists(repomd_path))
        ftypes = util.get_repomd_filetypes(repomd_path)
        assert('product' in ftypes)

        # validate isos are generated
        iso_dir = os.path.join(tgt_dir, 'isos')
        assert(os.path.exists(iso_dir))
        iso_list = os.listdir(iso_dir)
        self.assertEquals(len(iso_list), 1)

    def _perform_sync(self, r):
        sync_tasks = []
        t = repo_sync.sync(r["id"])
        sync_tasks.append(t)
        # Poll tasks and wait for sync to finish
        waiting_tasks = [t.id for t in sync_tasks]
        while len(waiting_tasks) > 0:
            time.sleep(1)
            for t_id in waiting_tasks:
                found_tasks = async.find_async(id=t_id)
                self.assertEquals(len(found_tasks), 1)
                updated_task = found_tasks[0]
                if updated_task.state in task.task_complete_states:
                    self.assertEquals(updated_task.state, task.task_finished)
                    waiting_tasks.remove(t_id)