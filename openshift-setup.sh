#!/bin/bash

# Clone and install grinder
cd $OPENSHIFT_DATA_DIR
git clone git://git.fedorahosted.org/git/grinder.git
cd $OPENSHIFT_DATA_DIR/grinder
~/$OPENSHIFT_APP_NAME/virtenv/bin/python setup.py install

# Clone and install gofer
cd $OPENSHIFT_DATA_DIR
git clone git://git.fedorahosted.org/git/gofer.git
cd $OPENSHIFT_DATA_DIR/gofer/src
~/$OPENSHIFT_APP_NAME/virtenv/bin/python setup.py install

# Download source and install qpid-python
cd $OPENSHIFT_DATA_DIR
wget http://mirrors.gigenet.com/apache/qpid/0.16/qpid-python-0.16.tar.gz
tar xf $OPENSHIFT_DATA_DIR/qpid-python-0.16.tar.gz
cd $OPENSHIFT_DATA_DIR/qpid-0.16/python
~/$OPENSHIFT_APP_NAME/virtenv/bin/python setup.py install

cd $OPENSHIFT_DATA_DIR

# Run pulp-migrate to create pulp_database in mongo
PYTHONPATH=$OPENSHIFT_REPO_DIR/wsgi:$OPENSHIFT_REPO_DIR/libs ~/$OPENSHIFT_APP_NAME/virtenv/bin/python $OPENSHIFT_REPO_DIR/platform/bin/pulp-migrate

# Add the defined user/password to pulp_database
mongo -u $OPENSHIFT_NOSQL_DB_USERNAME -p $OPENSHIFT_NOSQL_DB_PASSWORD $OPENSHIFT_NOSQL_DB_HOST:$OPENSHIFT_NOSQL_DB_PORT/admin <<EOQ
use pulp_database
db.addUser("admin", "${OPENSHIFT_NOSQL_DB_PASSWORD}")
EOQ

# Symlink repos to the static directory
ln -s $OPENSHIFT_DATA_DIR/var/www/pub/https/repos $OPENSHIFT_REPO_DIR/wsgi/static/repos

# Restart app
$OPENSHIFT_GEAR_DIR/${OPENSHIFT_APP_NAME}_ctl.sh restart



