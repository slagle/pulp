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
_devel = pulp_top_dir == "/"
    
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
    "/var/run/httpd",
    "/var/log/httpd",
    )

DEVEL_FILES = (
    ('/etc/httpd/conf', 'etc/httpd/conf'),
    ('/etc/httpd/conf/httpd.conf', 'etc/httpd/conf/httpd.conf'),
    ('/etc/httpd/conf.d', 'etc/httpd/conf.d'),
    ('platform/etc/pulp/admin/admin.conf', 'etc/pulp/admin/admin.conf'),
    ('platform/etc/pulp/server.conf', 'etc/pulp/server.conf'),
    ('platform/etc/httpd/conf.d/pulp.conf', 'etc/httpd/conf.d/pulp.conf'),
    ('rpm-support/etc/httpd/conf.d/pulp_rpm.conf', 'etc/httpd/conf.d/pulp_rpm.conf'),
    ('platform/srv/pulp/webservices.wsgi', 'srv/pulp/webservices.wsgi'),
    )

DEVEL_LINKS = (
    ('var/log/httpd', 'etc/httpd/logs'),
    ('var/run/httpd', 'etc/httpd/run'),
    ('/usr/lib64/httpd/modules', 'etc/httpd/modules'),
    )

REPLACE_PATHS = (
    "/srv/pulp/webservices.wsgi",
    "/etc/pki/pulp/ca.crt",
    "/var/www/pub/http/repos",
    "/var/www/pub/https/repos",
    "/var/www/pub/gpg",
    "/var/www/pub/ks",
    "/srv/pulp/repo_auth.wsgi",
    "/etc/httpd",
    "/usr/lib/pulp/admin/extensions",
    "/etc/pulp/logging/basic.cfg",
    "/var/log/pulp/pulp.log",
    "/var/log/pulp/grinder.log",
    "/etc/pki/pulp/ca.key",
    "/etc/pki/pulp/ssl_ca.crt",
    )

PORT_FILES = (
    "/etc/httpd/conf/httpd.conf",
    "/etc/httpd/conf.d/pulp_rpm.conf",
    "/etc/httpd/conf.d/ssl.conf",
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

    if _devel:
        devel(opts)

    return os.EX_OK

def devel(opts):

    os.system("virtualenv --system-site-packages %s" % pulp_top_dir)

    for dir in DEVEL_DIRS:
        new_dir_path = os.path.join(pulp_top_dir, dir[1:])
        if os.path.exists(new_dir_path):
            shutil.rmtree(new_dir_path)
        os.mkdir(new_dir_path)

    for src, dst in DEVEL_FILES:
        dst = os.path.join(pulp_top_dir, dst)
        if os.path.exists(dst):
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            else:
                os.unlink(dst)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copyfile(src, dst)

        for path in REPLACE_PATHS:
            new_path = os.path.join(pulp_top_dir, path[1:])
            print "replacing %s with %s in %s" \
                % (path, new_path, dst)
            os.system("sed -i 's#%s#%s#g' %s" % 
                (path, new_path, dst))

    for src, dst in DEVEL_LINKS:
        dst = os.path.join(pulp_top_dir, dst)
        if os.path.exists(dst):
            os.unlink(dst)
        if not src.startswith('/'):
            src = os.path.join(pulp_top_dir, src)
        if os.path.exists(dst):
            os.unlink(dst)
        print "creating link: %s" % dst
        os.symlink(src, dst)

    for port_file in PORT_FILES:
        port_file_path = os.path.join(pulp_top_dir, port_file[1:])
        os.system("sed -i 's#80#8080#g' %s" % port_file_path)
        os.system("sed -i 's#443#8443#g' %s" % port_file_path)

    virtualenv_setup = """activate_this = '%s/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
""" % pulp_top_dir

    wsgi_path = os.path.join(pulp_top_dir, "srv/pulp/webservices.wsgi")
    f = open(wsgi_path)
    old_lines = f.read().split('\n')
    f.close()
    f = open(wsgi_path, 'w')
    comments = 0
    for old_line in old_lines:
        if old_line.startswith('#'):
            f.write('%s\n' % old_line)
            comments += 1
        else:
            break

    f.write(virtualenv_setup)

    for old_line in old_lines[comments:]:
        f.write('%s\n' % old_line)

    f.close()

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
