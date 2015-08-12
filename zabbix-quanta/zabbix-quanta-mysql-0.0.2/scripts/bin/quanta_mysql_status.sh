#!/bin/sh
#
# Simple script to retrieve info from mysql SHOW STATUS query.
# Copyright Quanta Computing 2015
#
# Usage: quanta_mysql_status.sh <metric>
#

# Check parameters
if [ -z "$1" ]; then
  echo "Usage: quanta_mysql_status.sh <metric>" >&2
  exit 1
fi
METRIC="$1"


# Load config
if [ -f /var/lib/zabbix/quanta/etc/quanta_mysql ]; then
  . /var/lib/zabbix/quanta/etc/quanta_mysql
fi

# Fallback to defaults if not configured properly
if [ -z "$MYSQL_TIMEOUT" ]; then
  MYSQL_TIMEOUT=3
fi

if [ -z "$MYSQL_USER" ] || [ -z "$MYSQL_PASSWORD" ]; then
  echo "Missing username or password in /var/lib/zabbix/quanta/etc/quanta_mysql" >&2
  exit 1
fi

MYSQL_BIN="/usr/bin/mysql"
if [ ! -x $MYSQL_BIN ]; then
  MYSQL_BIN=`which mysql`
fi

echo "SHOW GLOBAL STATUS WHERE Variable_name='$METRIC';" \
 | $MYSQL_BIN --connect_timeout=$MYSQL_TIMEOUT -N -u $MYSQL_USER --password="$MYSQL_PASSWORD" \
 | /usr/bin/awk '{print $2}'
