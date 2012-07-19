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
import pwd
import shutil
import sys

pulp_top_dir = os.environ.get("PULP_TOP_DIR", "/")
_devel = pulp_top_dir != "/"
    
pulp_log_dir = os.path.join(pulp_top_dir, "var/log/pulp")
pulp_lib_dir = os.path.join(pulp_top_dir, "var/lib/pulp")
pulp_pki_dir = os.path.join(pulp_top_dir, "etc/pki/pulp")
pub_dir = os.path.join(pulp_top_dir, "var/www/pub")

DIRS = (
    '/etc',
    '/etc/bash_completion.d',
    '/etc/httpd',
    '/etc/httpd/conf.d',
    '/etc/pulp',
    '/etc/pulp/admin',
    '/etc/pulp/admin/conf.d',
    '/etc/pulp/consumer',
    '/etc/pulp/consumer/conf.d',
    '/etc/pulp/distributor',
    '/etc/pulp/importer',
    '/etc/pulp/agent',
    '/etc/pulp/agent/conf.d',
    '/etc/gofer',
    '/etc/gofer/plugins',
    '/etc/pki/pulp',
    '/etc/pki/pulp/content',
    '/etc/rc.d/init.d',
    '/etc/yum/pluginconf.d',
    '/srv',
    '/srv/pulp',
    '/usr/bin',
    '/usr/lib/pulp/',
    '/usr/lib/pulp/agent',
    '/usr/lib/pulp/agent/handlers',
    '/usr/lib/pulp/admin',
    '/usr/lib/pulp/admin/extensions',
    '/usr/lib/pulp/consumer',
    '/usr/lib/pulp/consumer/extensions',
    '/usr/lib/gofer',
    '/usr/lib/gofer/plugins',
    '/usr/lib/yum-plugins/',
    '/var/lib/pulp',
    '/var/lib/pulp_client',
    '/var/lib/pulp_client/admin',
    '/var/lib/pulp_client/admin/extensions',
    '/var/lib/pulp_client/consumer',
    '/var/lib/pulp_client/consumer/extensions',
    '/usr/lib/pulp/plugins',
    '/usr/lib/pulp/plugins/distributors',
    '/usr/lib/pulp/plugins/importers',
    '/usr/lib/pulp/plugins/profilers',
    '/usr/lib/pulp/plugins/types',
    '/var/lib/pulp/published',
    '/var/lib/pulp/published/http',
    '/var/lib/pulp/published/https',
    '/var/lib/pulp/uploads',
    '/var/log/pulp',
    '/var/www/.python-eggs', # needed for older versions of mod_wsgi
    '/var/run',
)

#
# Str entry assumes same src and dst relative path.
# Tuple entry is explicit (src, dst)
#
# Please keep alphabetized and by subproject

# Standard directories
DIR_ADMIN_EXTENSIONS = '/usr/lib/pulp/admin/extensions/'
DIR_CONSUMER_EXTENSIONS = '/usr/lib/pulp/consumer/extensions/'
DIR_PLUGINS = '/usr/lib/pulp/plugins'

LINKS = (
    ('builtins/extensions/admin/pulp_admin_auth', DIR_ADMIN_EXTENSIONS + 'pulp_admin_auth'),
    ('builtins/extensions/admin/pulp_admin_consumer', DIR_ADMIN_EXTENSIONS + 'pulp_admin_consumer'),
    ('builtins/extensions/admin/pulp_repo', DIR_ADMIN_EXTENSIONS + 'pulp_repo'),
    ('builtins/extensions/admin/pulp_server_info', DIR_ADMIN_EXTENSIONS + 'pulp_server_info'),
    ('builtins/extensions/admin/pulp_tasks', DIR_ADMIN_EXTENSIONS + 'pulp_tasks'),
    ('builtins/extensions/admin/pulp_upload', DIR_ADMIN_EXTENSIONS + 'pulp_upload'),

    ('builtins/extensions/consumer/pulp_consumer', DIR_CONSUMER_EXTENSIONS + 'pulp_consumer'),

    ('platform/bin/pulp-admin', '/usr/bin/pulp-admin'),
    ('platform/bin/pulp-consumer', '/usr/bin/pulp-consumer'),
    ('platform/bin/pulp-migrate', '/usr/bin/pulp-migrate'),

    ('platform/etc/bash_completion.d/pulp-admin', '/etc/bash_completion.d/pulp-admin'),
    ('platform/etc/httpd/conf.d/pulp.conf', '/etc/httpd/conf.d/pulp.conf'),
    ('platform/etc/gofer/plugins/pulp.conf', '/etc/gofer/plugins/pulp.conf'),
    ('platform/etc/pki/pulp/ca.key', '/etc/pki/pulp/ca.key'),
    ('platform/etc/pki/pulp/ca.crt', '/etc/pki/pulp/ca.crt'),
    ('platform/etc/pulp/server.conf', '/etc/pulp/server.conf'),
    ('platform/etc/pulp/admin/admin.conf', '/etc/pulp/admin/admin.conf'),
    ('platform/etc/pulp/consumer/consumer.conf', '/etc/pulp/consumer/consumer.conf'),
    ('platform/etc/pulp/logging', '/etc/pulp/logging'),
    ('platform/etc/rc.d/init.d/pulp-server', '/etc/rc.d/init.d/pulp-server'),

    ('platform/src/pulp/agent/gofer/pulp.py', '/usr/lib/gofer/plugins/pulp.py'),
    ('platform/srv/pulp/webservices.wsgi', '/srv/pulp/webservices.wsgi'),

    ('rpm-support/etc/httpd/conf.d/pulp_rpm.conf', '/etc/httpd/conf.d/pulp_rpm.conf'),
    ('rpm-support/etc/pulp/repo_auth.conf', '/etc/pulp/repo_auth.conf'),
    ('rpm-support/etc/pulp/agent/conf.d/rpm.conf', '/etc/pulp/agent/conf.d/rpm.conf'),
    ('rpm-support/etc/pulp/agent/conf.d/bind.conf', '/etc/pulp/agent/conf.d/bind.conf'),
    ('rpm-support/etc/pulp/agent/conf.d/linux.conf', '/etc/pulp/agent/conf.d/linux.conf'),
    ('rpm-support/etc/yum/pluginconf.d/pulp-profile-update.conf', '/etc/yum/pluginconf.d/pulp-profile-update.conf'),

    ('rpm-support/extensions/admin/rpm_admin_consumer', DIR_ADMIN_EXTENSIONS + 'rpm_admin_consumer'),
    ('rpm-support/extensions/admin/rpm_repo', DIR_ADMIN_EXTENSIONS + 'rpm_repo'),
    ('rpm-support/extensions/admin/rpm_sync', DIR_ADMIN_EXTENSIONS + 'rpm_sync'),
    ('rpm-support/extensions/admin/rpm_units_copy', DIR_ADMIN_EXTENSIONS + 'rpm_units_copy'),
    ('rpm-support/extensions/admin/rpm_units_search', DIR_ADMIN_EXTENSIONS + 'rpm_units_search'),
    ('rpm-support/extensions/admin/rpm_upload', DIR_ADMIN_EXTENSIONS + 'rpm_upload'),
    ('rpm-support/extensions/admin/rpm_package_group_upload', DIR_ADMIN_EXTENSIONS + 'rpm_package_group_upload'),

    ('rpm-support/extensions/consumer/rpm_consumer', DIR_CONSUMER_EXTENSIONS + 'rpm_consumer'),

    ('rpm-support/handlers/rpm.py', '/usr/lib/pulp/agent/handlers/rpm.py'),
    ('rpm-support/handlers/bind.py', '/usr/lib/pulp/agent/handlers/bind.py'),
    ('rpm-support/handlers/linux.py', '/usr/lib/pulp/agent/handlers/linux.py'),

    ('rpm-support/plugins/types/rpm_support.json', DIR_PLUGINS + '/types/rpm_support.json'),
    ('rpm-support/plugins/importers/yum_importer', DIR_PLUGINS + '/importers/yum_importer'),
    ('rpm-support/plugins/distributors/yum_distributor', DIR_PLUGINS + '/distributors/yum_distributor'),

    ('rpm-support/src/pulp/client/consumer/yumplugin/pulp-profile-update.py', '/usr/lib/yum-plugins/pulp-profile-update.py'),
    ('rpm-support/srv/pulp/repo_auth.wsgi', '/srv/pulp/repo_auth.wsgi'),
    )

DEVEL_DIRS = (
    "var/run/httpd",
    "var/log/httpd",
    "src",
    )

DEVEL_FILES = (
    ('/etc/httpd/conf', 'etc/httpd/conf'),
    ('/etc/httpd/conf/httpd.conf', 'etc/httpd/conf/httpd.conf'),
    ('/etc/httpd/conf.d', 'etc/httpd/conf.d'),
    ('/usr/lib64/httpd/modules', 'etc/httpd/modules'),
    ('platform/etc/pulp/admin/admin.conf', 'etc/pulp/admin/admin.conf'),
    ('platform/etc/pulp/server.conf', 'etc/pulp/server.conf'),
    ('platform/etc/httpd/conf.d/pulp.conf', 'etc/httpd/conf.d/pulp.conf'),
    ('rpm-support/etc/httpd/conf.d/pulp_rpm.conf', 'etc/httpd/conf.d/pulp_rpm.conf'),
    ('platform/srv/pulp/webservices.wsgi', 'srv/pulp/webservices.wsgi'),
    ('platform/bin/pulp-admin', 'usr/bin/pulp-admin'),
    )

DEVEL_SOURCE_LINKS = (
    ('platform/src/pulp', 'src/pulp'),
    ('rpm-support/src/pulp_rpm', 'src/pulp_rpm'),
    )

DEVEL_PULP_TOP_DIR_LINKS = (
    ('var/log/httpd', 'etc/httpd/logs'),
    ('var/run/httpd', 'etc/httpd/run'),
    )

REPLACE_PATHS = (
    "srv/pulp/webservices.wsgi",
    "etc/pki/pulp/ca.crt",
    "var/www/pub/http/repos",
    "var/www/pub/https/repos",
    "var/www/pub/gpg",
    "var/www/pub/ks",
    "srv/pulp/repo_auth.wsgi",
    "etc/httpd",
    "usr/lib/pulp/admin/extensions",
    "etc/pulp/logging/basic.cfg",
    "var/log/pulp/pulp.log",
    "var/log/pulp/grinder.log",
    "etc/pki/pulp/ca.key",
    "etc/pki/pulp/ssl_ca.crt",
    )

PORT_FILES = (
    "etc/httpd/conf/httpd.conf",
    "etc/httpd/conf.d/pulp_rpm.conf",
    "etc/httpd/conf.d/ssl.conf",
    "etc/pulp/admin/admin.conf",
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
    parser.add_option('-A', '--apache-user',
                      action='store',
                      help=('system user that will be running apache '
                           '(defaults to apache)')
                     )

    parser.set_defaults(install=False,
                        uninstall=False,
                        debug=True)

    opts, args = parser.parse_args()

    if opts.install and opts.uninstall:
        parser.error('both install and uninstall specified')

    if not (opts.install or opts.uninstall):
        parser.error('neither install or uninstall specified')

    if not opts.apache_user:
        opts.apache_user = 'apache'

    return (opts, args)


def debug(opts, msg):
    if not opts.debug:
        return
    sys.stderr.write('%s\n' % msg)


def create_dirs(opts):
    for d in DIRS:
        if d.startswith('/'):
            d = d[1:]
        d = os.path.join(pulp_top_dir, d)
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
        dst = os.path.join(pulp_top_dir, dst)
        links.append((src, dst))
    return links


def install(opts):

    if _devel:
        devel(opts)

    create_dirs(opts)

    currdir = os.path.abspath(os.path.dirname(__file__))
    for src, dst in getlinks():
        debug(opts, 'creating link: %s' % dst)
        target = os.path.join(currdir, src)
        try:
            os.symlink(target, dst)
        except OSError, e:
            if e.errno != 17:
                raise
            debug(opts, '%s exists, skipping' % dst)
            continue

    # Link between pulp and apache
    if not os.path.exists(pub_dir):
        os.symlink(os.path.join(pulp_lib_dir, "published"), pub_dir)

    # Grant write access to the pulp tools log file and pulp
    # packages dir for the apache user
    uid, gid = pwd.getpwnam(opts.apache_user)[2:4]

    os.system('chown -R %s:%s %s' % (uid, gid, pulp_log_dir))
    os.system('chown -R %s:%s %s' % (uid, gid, pulp_lib_dir))
    os.system('chown -R %s:%s %s' % (uid, gid, os.path.join(pulp_lib_dir, 'published')))
    # guarantee apache always has write permissions
    os.system('chmod 3775 %s' % pulp_log_dir)
    os.system('chmod 3775 %s' % pulp_lib_dir)
    # Update for certs
    os.system('chown -R %s:%s %s' % (uid, gid, pulp_pki_dir))

    return os.EX_OK

def devel(opts):

    # Create pulp_top_dir if it doesn't exist
    if not os.path.exists(pulp_top_dir):
        os.makedirs(pulp_top_dir)

    # Create development directories if they don't already exist
    for _dir in DEVEL_DIRS:
        new_dir = os.path.join(pulp_top_dir, _dir)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)

    # Copy development files/directories if they don't already exist
    # These files are copied instead of symlink'd b/c we're going to modify
    # them.
    for src, dst in DEVEL_FILES:
        new_dst = os.path.join(pulp_top_dir, dst)
        if not os.path.exists(new_dst):
            if os.path.isdir(src):
                shutil.copytree(src, new_dst)
            else:
                # Create directory to the file if needed
                _dir = os.path.dirname(new_dst)
                if not os.path.exists(_dir):
                    os.makedirs(_dir)
                shutil.copy(src, new_dst)

        if not os.path.isdir(new_dst):
            # Substitute needed paths
            for path in REPLACE_PATHS:
                new_path = os.path.join(pulp_top_dir, path)
                command = "sed -i 's#%s#%s#g' %s" % (path, new_path, new_dst)
                print "running %s" % command
                os.system(command)

    # Symlink needed files from the source tree
    for src, dst in DEVEL_SOURCE_LINKS:
        new_dst = os.path.join(pulp_top_dir, dst)
        currdir = os.path.abspath(os.path.dirname(__file__))
        new_src = os.path.join(currdir, src)
        if not os.path.exists(new_dst):
            print "linking %s to %s" % (new_dst, new_src)
            os.symlink(new_src, new_dst)

    # Symlink needed files within pulp_top_dir
    for src, dst in DEVEL_PULP_TOP_DIR_LINKS:
        new_dst = os.path.join(pulp_top_dir, dst)
        new_src = os.path.join(pulp_top_dir, src)
        if not os.path.exists(new_dst):
            print "linking %s to %s" % (new_dst, new_src)
            os.symlink(new_src, new_dst)

    # Port substitution
    for port_file in PORT_FILES:
        port_file_path = os.path.join(pulp_top_dir, port_file)
        os.system("sed -i 's#80#8080#g' %s" % port_file_path)
        os.system("sed -i 's#443#8443#g' %s" % port_file_path)

    # Modify import path 
    src_dir = os.path.join(pulp_top_dir, "src").replace('/', '\/')
    wsgi_path = os.path.join(pulp_top_dir, "srv/pulp/webservices.wsgi")
    pulp_admin_path = os.path.join(pulp_top_dir, "usr/bin/pulp-admin")
    sed = \
        "sed -i '0,/^$/s/^$/import sys\\nsys.path.insert(0, \"%s\")\\n/' %s"
    command = sed % (src_dir, wsgi_path)
    os.system(command)
    command = sed % (src_dir, pulp_admin_path)
    os.system(command)

    # Modify hostname in admin.conf
    pulp_admin_conf_path = os.path.join(pulp_top_dir,
        'etc/pulp/admin/admin.conf')
    import socket
    hostname = socket.gethostname()
    os.system("sed -i 's/localhost.localdomain/%s/' %s" % 
        (hostname, pulp_admin_conf_path))


def uninstall(opts):
    for src, dst in getlinks():
        debug(opts, 'removing link: %s' % dst)
        if not os.path.islink(dst):
            debug(opts, '%s does not exist, skipping' % dst)
            continue
        os.unlink(dst)

    # Link between pulp and apache
    if os.path.exists(pub_dir):
        os.unlink(pub_dir)

    # Old link between pulp and apache, make sure it's cleaned up
    if os.path.exists(os.path.join(pulp_top_dir, 'var/www/html/pub')):
        os.unlink(os.path.join(pulp_top_dir, 'var/www/html/pub'))

    return os.EX_OK

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # TODO add something to check for permissions
    opts, args = parse_cmdline()
    if opts.install:
        sys.exit(install(opts))
    if opts.uninstall:
        sys.exit(uninstall(opts))
