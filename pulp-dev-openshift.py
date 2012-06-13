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

import optparse
import os
import shutil
import sys

data_dir = os.environ["OPENSHIFT_DATA_DIR"]
log_dir = os.path.join(data_dir, "var/log")
pulp_log_dir = os.path.join(log_dir, "pulp")
lib_dir = os.path.join(data_dir, "var/lib")
pulp_lib_dir = os.path.join(lib_dir, "pulp")
pki_dir = os.path.join(data_dir, "etc/pki")
pulp_pki_dir = os.path.join(pki_dir, "pulp")

DIRS = (
    '/etc',
    '/etc/bash_completion.d',
    '/etc/pulp',
    '/etc/pulp/admin',
    '/etc/pulp/consumer',
    '/etc/pulp/distributor',
    '/etc/pulp/importer',
    '/etc/pulp/agent',
    '/etc/pulp/agent/handler',
    '/etc/gofer',
    '/etc/gofer/plugins',
    '/etc/pki/pulp',
    '/etc/pki/pulp/content',
    '/var/lib/pulp',
    '/var/lib/pulp_client',
    '/var/lib/pulp_client/admin',
    '/var/lib/pulp_client/admin/extensions',
    '/var/lib/pulp_client/consumer',
    '/var/lib/pulp_client/consumer/extensions',
    '/var/lib/pulp/plugins',
    '/var/lib/pulp/plugins/distributors',
    '/var/lib/pulp/plugins/importers',
    '/var/lib/pulp/plugins/profilers',
    '/var/lib/pulp/plugins/types',
    '/var/lib/pulp/published',
    '/var/lib/pulp/published/http',
    '/var/lib/pulp/published/https',
    '/var/lib/pulp/uploads',
    '/var/log/pulp',
)

#
# Str entry assumes same src and dst relative path.
# Tuple entry is explicit (src, dst)
#
LINKS = (
    'etc/bash_completion.d/pulp-admin',
    'etc/pulp/server.conf',
    'etc/pulp/repo_auth.conf',
    'etc/pulp/admin/admin.conf',
    'etc/pulp/admin/task.conf',
    'etc/pulp/admin/job.conf',
    'etc/pulp/admin/v2_admin.conf',
    'etc/pulp/consumer/consumer.conf',
    'etc/pulp/consumer/v2_consumer.conf',
    'etc/pulp/agent/handler/rpm.conf',
    'etc/pulp/agent/handler/bind.conf',
    'etc/pulp/agent/handler/linux.conf',
    'etc/pki/pulp/ca.key',
    'etc/pki/pulp/ca.crt',
    'etc/gofer/plugins/pulp.conf',
    'etc/gofer/plugins/pulpplugin.conf',
    'etc/gofer/plugins/consumer.conf',
    'etc/pulp/logging',
    ('extensions/pulp_admin_auth', '/var/lib/pulp_client/admin/extensions/pulp_admin_auth'),
    ('extensions/pulp_admin_consumer', '/var/lib/pulp_client/admin/extensions/pulp_admin_consumer'),
    ('extensions/pulp_consumer', '/var/lib/pulp_client/consumer/extensions/pulp_consumer'),
    ('extensions/pulp_repo', '/var/lib/pulp_client/admin/extensions/pulp_repo'),
    ('extensions/pulp_server_info', '/var/lib/pulp_client/admin/extensions/pulp_server_info'),
    ('extensions/pulp_tasks', '/var/lib/pulp_client/admin/extensions/pulp_tasks'),
    ('extensions/rpm_admin_consumer', '/var/lib/pulp_client/admin/extensions/rpm_admin_consumer'),
    ('extensions/rpm_repo', '/var/lib/pulp_client/admin/extensions/rpm_repo'),
    ('extensions/rpm_sync', '/var/lib/pulp_client/admin/extensions/rpm_sync'),
    ('extensions/rpm_units_copy', '/var/lib/pulp_client/admin/extensions/rpm_units_copy'),
    ('extensions/rpm_units_search', '/var/lib/pulp_client/admin/extensions/rpm_units_search'),
    ('extensions/rpm_upload', '/var/lib/pulp_client/admin/extensions/rpm_upload'),
    ('plugins/types/rpm.json', '/var/lib/pulp/plugins/types/rpm.json'),
    ('plugins/types/srpm.json', '/var/lib/pulp/plugins/types/srpm.json'),
    ('plugins/types/erratum.json', '/var/lib/pulp/plugins/types/erratum.json'),
    ('plugins/types/drpm.json', '/var/lib/pulp/plugins/types/drpm.json'),
    ('plugins/types/distribution.json', '/var/lib/pulp/plugins/types/distribution.json'),
    ('plugins/importers/yum_importer', '/var/lib/pulp/plugins/importers/yum_importer'),
    ('plugins/distributors/yum_distributor', '/var/lib/pulp/plugins/distributors/yum_distributor'),
    )

def parse_cmdline():
    """
    Parse and validate the command line options.
    """
    parser = optparse.OptionParser()

    parser.add_option('-I', '--install',
                      action='store_true',
                      help='install pulp development files')
    parser.add_option('-U', '--uninstall',
                      action='store_true',
                      help='uninstall pulp development files')
    parser.add_option('-D', '--debug',
                      action='store_true',
                      help=optparse.SUPPRESS_HELP)

    parser.set_defaults(install=False,
                        uninstall=False,
                        debug=True)

    opts, args = parser.parse_args()

    if opts.install and opts.uninstall:
        parser.error('both install and uninstall specified')

    if not (opts.install or opts.uninstall):
        parser.error('neither install or uninstall specified')

    return (opts, args)


def debug(opts, msg):
    if not opts.debug:
        return
    sys.stderr.write('%s\n' % msg)


def create_dirs(opts):
    for d in DIRS:
        if d.startswith('/'):
            d = d[1:]
        d = os.path.join(data_dir, d)
        debug(opts, 'creating directory: %s' % d)
        if os.path.exists(d) and os.path.isdir(d):
            debug(opts, '%s exists, skipping' % d)
            continue
        os.makedirs(d, 0777)


def getlinks():
    links = []
    for l in LINKS:
        if isinstance(l, (list, tuple)):
            src = l[0]
            dst = l[1]
        else:
            src = l
            dst = os.path.join('/', l)
        if dst.startswith('/'):
            dst = dst[1:]
        dst = os.path.join(data_dir, dst)
        links.append((src, dst))
    return links


def install(opts):
    create_dirs(opts)
    currdir = os.path.abspath(os.path.dirname(__file__))
    for src, dst in getlinks():
        debug(opts, 'creating link: %s' % dst)
        try:
            os.symlink(os.path.join(currdir, src), dst)
        except OSError, e:
            if e.errno != 17:
                raise
            debug(opts, '%s exists, skipping' % dst)
            continue

    # Link between pulp and apache
    # TODO: Not sure if this is needed for OpenShift, comment out for now
    # if not os.path.exists('/var/www/pub'):
        # os.symlink('/var/lib/pulp/published', '/var/www/pub')

    # Grant apache write access to the pulp tools log file and pulp
    # packages dir

    # Use current user insetad of apache for OpenShift
    uid = os.getuid()
    gid = os.getgid()

    os.system('chown -R %s:%s %s' % (uid, gid, pulp_log_dir))
    os.system('chown -R %s:%s %s' % (uid, gid, pulp_lib_dir))
    # guarantee apache always has write permissions
    os.system('chmod 3775 %s' % pulp_log_dir)
    os.system('chmod 3775 %s' % pulp_lib_dir)
    # Update for certs
    os.system('chown -R %s:%s %s' % (uid, gid, pulp_pki_dir))

    # Disable existing SSL configuration
    #if os.path.exists('/etc/httpd/conf.d/ssl.conf'):
    #    shutil.move('/etc/httpd/conf.d/ssl.conf', '/etc/httpd/conf.d/ssl.off')

    return os.EX_OK


def uninstall(opts):
    for src, dst in getlinks():
        debug(opts, 'removing link: %s' % dst)
        if not os.path.exists(dst):
            debug(opts, '%s does not exist, skipping' % dst)
            continue
        os.unlink(dst)

    # Link between pulp and apache
    if os.path.exists('/var/www/pub'):
        os.unlink('/var/www/pub')

    # Old link between pulp and apache, make sure it's cleaned up
    if os.path.exists('/var/www/html/pub'):
        os.unlink('/var/www/html/pub')

    return os.EX_OK

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # TODO add something to check for permissions
    opts, args = parse_cmdline()
    if opts.install:
        sys.exit(install(opts))
    if opts.uninstall:
        sys.exit(uninstall(opts))
