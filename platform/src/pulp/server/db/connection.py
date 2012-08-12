# -*- coding: utf-8 -*-
#
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

import os

import logging
import time
from gettext import gettext as _

import pymongo
from pymongo.collection import Collection
from pymongo.errors import AutoReconnect
from pymongo.son_manipulator import AutoReference, NamespaceInjector

from pulp.server import config
from pulp.server.compat import wraps
from pulp.server.exceptions import PulpException

# globals ----------------------------------------------------------------------

_connection = None
_database = None

_log = logging.getLogger(__name__)

# connection api ---------------------------------------------------------------

def initialize(name=None, seeds=None):
    """
    Initialize the connection pool and top-level database for pulp.
    """
    global _connection, _database
    try:
        if not name:
            name = config.config.get('database', 'name')
        if not seeds:
            seeds = config.config.get('database', 'seeds')
        _log.info("Attempting Database connection with seeds = %s" % (seeds))
        _connection = pymongo.Connection(seeds)
        _database = getattr(_connection, name)
        _database.add_son_manipulator(NamespaceInjector())
        _database.add_son_manipulator(AutoReference(_database))
        _log.info("Database connection established with: seeds = %s, name = %s" % (seeds, name))
    except Exception:
        _log.critical('Database initialization failed')
        _connection = None
        _database = None
        raise

# collection wrapper class -----------------------------------------------------

class PulpCollectionFailure(PulpException):
    """
    Exceptions generated by the PulpCollection class
    """
    pass


def _retry_decorator(method):
    """
    Collection instance method decorator providing retry support for pymongo
    AutoReconnect exceptions
    """
    # 'self' is not passed into the method below as the super call in the
    # constructor has already bound self to the method
    self = method.im_self
    @wraps(method)
    def retry(*args, **kwargs):
        tries = 0
        while tries <= self.retries:
            try:
                return method(*args, **kwargs)
            except AutoReconnect:
                tries += 1
                _log.warn(_('%s operation failed on %s: tries remaining: %d') %
                          (method.__name__, self.full_name, self.retries - tries + 1))
                if tries <= self.retries:
                    time.sleep(0.3)
        raise PulpCollectionFailure(
            _('%s operation failed on %s: database connection still down after %d tries') %
            (method.__name__, self.full_name, (self.retries + 1)))
    return retry


class PulpCollection(Collection):
    """
    pymongo.collection.Collection wrapper that provides support for retries when
    pymongo.errors.AutoReconnect exception is raised
    """

    _retry_methods = ('insert', 'save', 'update', 'remove', 'drop', 'find',
                      'find_one', 'count', 'create_index', 'ensure_index',
                      'drop_index', 'drop_indexes', 'group', 'rename',
                      'map_reduce')

    def __init__(self, database, name, create=False, retries=0, **kwargs):
        super(PulpCollection, self).__init__(database, name, create=create, **kwargs)
        self.retries = retries
        for m in self._retry_methods:
            setattr(self, m, _retry_decorator(getattr(self, m)))

    def __getstate__(self):
        return {'name': self.name}

    def __setstate__(self, state):
        return get_collection(state['name'])

    def query(self, criteria):
        """
        Run a query with a Pulp custom query object
        @param criteria: Criteria object specifying the query to run
        @type  criteria: L{pulp.server.db.model.criteria.Criteria}
        @return: pymongo cursor for the given query
        @rtype:  L{pymongo.cursor.Cursor}
        """
        cursor = self.find(criteria.spec, fields=criteria.fields)
        if criteria.sort is not None:
            for entry in criteria.sort:
                cursor.sort(*entry)
        if criteria.skip is not None:
            cursor.skip(criteria.skip)
        if criteria.limit is not None:
            cursor.limit(criteria.limit)
        return cursor

# -- public --------------------------------------------------------------------

def get_collection(name, create=False):
    """
    Factory function to instantiate PulpConnection objects using configurable
    parameters.
    """
    global _database
    if _database is None:
        raise PulpCollectionFailure(_('Cannot get collection from uninitialized database'))
    retries = config.config.getint('database', 'operation_retries')
    return PulpCollection(_database, name, retries=retries, create=create)

def database():
    """
    @return: reference to the mongo database being used by the server
    @rtype:  L{pymongo.database.Database}
    """
    return _database
