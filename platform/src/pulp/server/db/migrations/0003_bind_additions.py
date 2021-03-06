# -*- coding: utf-8 -*-
# Copyright (c) 2013 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

from pulp.server.db.model.consumer import Bind


def migrate(*args, **kwargs):
    """
    Adds attributes needed for binding configurations. To maintain backward compatibility,
    the notify_agent field is set to True.
    """

    additions = (
        ('notify_agent', True),
        ('binding_config', None),
    )
    collection = Bind.get_collection()
    for bind in collection.find({}):
        dirty = False
        for key, value in additions:
            if key not in bind:
                bind[key] = value
                dirty = True
        if dirty:
            collection.save(bind, safe=True)

