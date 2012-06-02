#
# Copyright (c) 2011 Red Hat, Inc.
#
# This software is licensed to you under the GNU Lesser General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (LGPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of LGPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/lgpl-2.0.txt.
#
# Jeff Ortel <jortel@redhat.com>
#

import os
import sys
import logging
from gofer import NAME
from logging import root, Formatter
from logging.handlers import RotatingFileHandler

LOGDIR = '/var/log/%s' % NAME
LOGFILE = 'agent.log'

TIME = '%(asctime)s'
LEVEL = ' [%(levelname)s]'
THREAD = '[%(threadName)s]'
FUNCTION = ' %(funcName)s()'
FILE = ' @ %(filename)s'
LINE = ':%(lineno)d'
MSG = ' - %(message)s'

if sys.version_info < (2,5):
    FUNCTION = ''

FMT = \
    ''.join((TIME,
            LEVEL,
            THREAD,
            FUNCTION,
            FILE,
            LINE,
            MSG,))

handler = None

def getLogger(name):
    global handler
    if not os.path.exists(LOGDIR):
        os.mkdir(LOGDIR)
    if handler is None:
        path = os.path.join(LOGDIR, LOGFILE)
        handler = RotatingFileHandler(path, maxBytes=0x100000, backupCount=5)
        handler.setFormatter(Formatter(FMT))
        root.setLevel(logging.INFO)
        root.addHandler(handler)
    log = logging.getLogger(name)
    return log
