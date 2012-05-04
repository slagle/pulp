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
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt

import os
from yum import YumBase
from optparse import OptionParser
from yum.plugins import TYPE_CORE, TYPE_INTERACTIVE
from pulp.client.agent.container import Handler
from pulp.client.agent.dispatcher import HandlerReport
from logging import getLogger, Logger

log = getLogger(__name__)

#
# Handlers
#

class Linux(Handler):
    """
    Linux content handler
    """

    def reboot(self, options):
        """
        Schedule a system reboot.
        @param options: An options dictionary
          - apply : apply the transaction
          - reboot : Reboot after installed 
        @type options: dict
        @return: True if scheduled
        @rtype: bool
        """
        scheduled = False
        opt = Options(options, apply=True, reboot=False)
        if opt.reboot:
            if opt.apply:
                os.system('shutdown -r +%d', minutes)
                log.info('rebooting in: %d minutes', minutes)
            scheduled = True
        return scheduled
            

class PackageHandler(Linux):
    """
    The package (rpm) content handler.
    @ivar cfg: configuration
    @type cfg: dict
    """

    def install(self, units, options):
        """
        Install content unit(s).
        @param units: A list of content unit_keys.
        @type units: list
        @param options: Unit install options.
          - apply : apply the transaction
          - importkeys : import GPG keys
          - reboot : Reboot after installed
        @type options: dict
        @return: An install report.  See: L{Package.install}
        @rtype: L{HandlerReport}
        """
        report = HandlerReport()
        opt = Options(options, apply=True, importkeys=False)
        pkg = Package(**opt)
        names = [key['name'] for key in units]
        details = pkg.install(names)
        report.succeeded(details)
        report.reboot_scheduled = self.reboot(options)
        return report

    def update(self, units, options):
        """
        Update content unit(s).
        @param units: A list of content unit_keys.
        @type units: list
        @param options: Unit update options.
          - apply : apply the transaction
          - importkeys : import GPG keys
          - reboot : Reboot after installed
        @type options: dict
        @return: An update report.  See: L{Package.update}
        @rtype: L{HandlerReport}
        """
        report = HandlerReport()
        opt = Options(options, apply=True, importkeys=False)
        pkg = Package(**opt)
        names = [key['name'] for key in units]
        details = pkg.update(names)
        report.succeeded(details)
        report.reboot_scheduled = self.reboot(options)
        return report

    def uninstall(self, units, options):
        """
        Uninstall content unit(s).
        @param units: A list of content unit_keys.
        @type units: list
        @param options: Unit uninstall options.
          - apply : apply the transaction
          - reboot : Reboot after installed
        @type options: dict
        @return: An uninstall report.  See: L{Package.uninstall}
        @rtype: L{HandlerReport}
        """
        report = HandlerReport()
        opt = Options(options, apply=True)
        pkg = Package(**opt)
        names = [key['name'] for key in units]
        details = pkg.uninstall(names)
        report.succeeded(details)
        report.reboot_scheduled = self.reboot(options)
        return report


class GroupHandler(Linux):
    """
    The package group content handler.
    @ivar cfg: configuration
    @type cfg: dict
    """

    def install(self, units, options):
        """
        Install content unit(s).
        @param units: A list of content unit_keys.
        @type units: list
        @param options: Unit install options.
        @type options: dict
        @return: An install report.
        @rtype: L{HandlerReport}
        """
        report = HandlerReport()
        opt = Options(options, apply=True, importkeys=False)
        grp = PackageGroup(**opt)
        names = [key['name'] for key in units]
        details = grp.install(names)
        report.succeeded(details)
        report.reboot_scheduled = self.reboot(options)
        return report

    def update(self, units, options):
        """
        Update content unit(s).
        @param units: A list of content unit_keys.
        @type units: list
        @param options: Unit update options.
        @type options: dict
        @return: An update report.
        @rtype: L{HandlerReport}
        """
        report = HandlerReport()
        opt = Options(options, apply=True, importkeys=False)
        grp = PackageGroup(**opt)
        names = [key['name'] for key in units]
        details = grp.update(names)
        report.succeeded(details)
        report.reboot_scheduled = self.reboot(options)
        return report

    def uninstall(self, units, options):
        """
        Uninstall content unit(s).
        @param units: A list of content unit_keys.
        @type units: list
        @param options: Unit uninstall options.
        @type options: dict
        @return: An uninstall report.
        @rtype: L{HandlerReport}
        """
        report = HandlerReport()
        opt = Options(options, apply=True)
        grp = PackageGroup(**opt)
        names = [key['name'] for key in units]
        details = grp.uninstall(names)
        report.succeeded(details)
        report.reboot_scheduled = self.reboot(options)
        return report

#
# options
#

class Options(dict):
    """
    Special dict capable of subsetting and defaulting.
    Also provides (.) notation accessors.
    """
    __getattr__ = dict.__getitem__

    def __init__(self, d, **subset):
        """
        @param d: A source dictionary.
        @type d: dict
        @param subset: keywords where keys specify
            the subset of keys and it's values define
            the default values.
            all keys.
        """
        dict.__init__(self)
        for k,v in subset.items():
            opt = d.get(k,v)
            self[k] = opt

#
# Implementation
#


class Yum(YumBase):
    """
    Provides custom configured yum object.
    """

    def __init__(self, importkeys=False):
        """
        @param importkeys: Allow the import of GPG keys.
        @type importkeys: bool
        """
        parser = OptionParser()
        parser.parse_args([])
        self.__parser = parser
        YumBase.__init__(self)
        self.preconf.optparser = self.__parser
        self.preconf.plugin_types = (TYPE_CORE, TYPE_INTERACTIVE)
        self.conf.assumeyes = importkeys

    def doPluginSetup(self, *args, **kwargs):
        """
        Set command line arguments.
        Support TYPE_INTERACTIVE plugins.
        """
        YumBase.doPluginSetup(self, *args, **kwargs)
        p = self.__parser
        options, args = p.parse_args([])
        self.plugins.setCmdLine(options, args)

    def registerCommand(self, command):
        """
        Support TYPE_INTERACTIVE plugins.
        Commands ignored.
        """
        pass

    def cleanLoggers(self):
        """
        Clean handlers leaked by yum.
        """
        for n,lg in Logger.manager.loggerDict.items():
            if not n.startswith('yum.'):
                continue
            for h in lg.handlers:
                lg.removeHandler(h)

    def close(self):
        """
        This should be handled by __del__() but YumBase
        objects never seem to completely go out of scope and
        garbage collected.
        """
        YumBase.close(self)
        self.closeRpmDB()
        self.cleanLoggers()


class Package:
    """
    Package management.
    Returned I{Package} NEVRA+ objects:
      - qname   : qualified name
      - repoid  : repository id
      - name    : package name
      - epoch   : package epoch
      - version : package version
      - release : package release
      - arch    : package arch
    """

    @classmethod
    def summary(cls, tsInfo, states=('i','u')):
        """
        Get transaction summary.
        @param tsInfo: A yum transaction.
        @type tsInfo: YumTransaction
        @param states: A list of yum transaction states.
        @type states: tuple|list
        @return: (resolved[],deps[])
        @rtype: tuple
        """
        resolved = []
        deps = []
        for t in tsInfo:
            if t.ts_state not in states:
                continue
            qname = str(t.po)
            package = dict(
                qname=qname,
                repoid=t.repoid,
                name=t.po.name,
                version=t.po.ver,
                release=t.po.rel,
                arch=t.po.arch,
                epoch=t.po.epoch)
            if t.isDep:
                deps.append(package)
            else:
                resolved.append(package)
        return (resolved, deps)

    @classmethod
    def installed(cls, tsInfo):
        """
        Get transaction summary for installed packages.
        @param tsInfo: A yum transaction.
        @type tsInfo: YumTransaction
        @return: (resolved[],deps[])
        @rtype: tuple
        """
        return cls.summary(tsInfo)

    @classmethod
    def erased(cls, tsInfo):
        """
        Get transaction summary for erased packages.
        @param tsInfo: A yum transaction.
        @type tsInfo: YumTransaction
        @return: (resolved[],deps[])
        @rtype: tuple
        """
        return cls.summary(tsInfo, ('e',))

    def __init__(self, apply=True, importkeys=False):
        """
        @param apply: Apply changes (not dry-run).
        @type apply: bool
        @param importkeys: Allow the import of GPG keys.
        @type importkeys: bool
        """
        self.apply = apply
        self.importkeys = importkeys

    def install(self, names):
        """
        Install packages by name.
        @param names: A list of package names.
        @type names: [str,]
        @return: Packages installed.
            {resolved=[Package,],deps=[Package,]}
        @rtype: dict
        """
        yb = Yum(self.importkeys)
        try:
            for info in names:
                yb.install(pattern=info)
            yb.resolveDeps()
            resolved, deps = self.installed(yb.tsInfo)
            if self.apply and resolved:
                yb.processTransaction()
        finally:
            yb.close()
        return dict(resolved=resolved, deps=deps)

    def uninstall(self, names):
        """
        Uninstall (erase) packages by name.
        @param names: A list of package names to be removed.
        @type names: list
        @return: Packages uninstalled (erased).
            {resolved=[Package,],deps=[Package,]}
        @rtype: dict
        """
        yb = Yum()
        try:
            for info in names:
                yb.remove(pattern=info)
            yb.resolveDeps()
            resolved, deps = self.erased(yb.tsInfo)
            if self.apply and resolved:
                yb.processTransaction()
        finally:
            yb.close()
        return dict(resolved=resolved, deps=deps)

    def update(self, names=None):
        """
        Update installed packages.
        When (names) is not specified, all packages are updated.
        @param names: A list of package names.
        @type names: [str,]
        @return: Packages installed (updated).
            {resolved=[Package,],deps=[Package,]}
        @rtype: dict
        """
        yb = Yum(self.importkeys)
        try:
            if names:
                for info in names:
                    yb.update(pattern=info)
            else:
                yb.update()
            yb.resolveDeps()
            resolved, deps = self.installed(yb.tsInfo)
            if self.apply and resolved:
                yb.processTransaction()
        finally:
            yb.close()
        return dict(resolved=resolved, deps=deps)


class PackageGroup:
    """
    PackageGroup management.
    """

    def __init__(self, apply=True, importkeys=False):
        """
        @param apply: Apply changes (not dry-run).
        @type apply: bool
        @param importkeys: Allow the import of GPG keys.
        @type importkeys: bool
        """
        self.apply = apply
        self.importkeys = importkeys

    def install(self, names):
        """
        Install package groups by name.
        @param names: A list of package group names.
        @type names: list
        @return: Packages installed.
            {resolved=[Package,],deps=[Package,]}
        @rtype: dict
        """
        yb = Yum(self.importkeys)
        try:
            for name in names:
                yb.selectGroup(name)
            yb.resolveDeps()
            resolved, deps = Package.installed(yb.tsInfo)
            if self.apply and resolved:
                yb.processTransaction()
        finally:
            yb.close()
        return dict(resolved=resolved, deps=deps)

    def uninstall(self, names):
        """
        Uninstall package groups by name.
        @param names: A list of package group names.
        @type names: [str,]
        @return: Packages uninstalled.
            {resolved=[Package,],deps=[Package,]}
        @rtype: dict
        """
        removed = {}
        yb = Yum()
        try:
            for name in names:
                yb.groupRemove(name)
            yb.resolveDeps()
            resolved, deps = Package.erased(yb.tsInfo)
            if self.apply and resolved:
                yb.processTransaction()
        finally:
            yb.close()
        return dict(resolved=resolved, deps=deps)