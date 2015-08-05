#!/bin/sh
#
# Simple script to retrieve info from apache status using netcat
# Copyright Quanta Computing 2015
#
# Usage: quanta_apache.sh <metric>
#

# Check parameters
if [ -z "$1" ]; then
  echo "Usage: quanta_apache.sh <metric>" >&2
  exit 1
fi
METRIC="$1"


# Load config
if [ -f /var/lib/zabbix/quanta/etc/quanta_apache ]; then
  . /var/lib/zabbix/quanta/etc/quanta_apache
fi

# Fallback to defaults if not configured properly
if [ -z "$APACHE_PORT" ]; then
  APACHE_PORT=80
fi
if [ -z "$APACHE_STATUS_URL" ]; then
  APACHE_STATUS_URL=/server-status
fi
if [ -z "$APACHE_STATUS_TIMEOUT" ]; then
  APACHE_STATUS_TIMEOUT=3
fi

APACHE_HOST=localhost

# Try to guess netcat binary path if not in /bin
NC_BIN=/bin/nc
if [ ! -x $NC_BIN ]; then
  NC_BIN=`which nc | head -1`
fi
if [ -z "$NC_BIN" ]; then
  echo "netcat binary not found" >&2
  exit 1
fi

# Magic takes place here
DATA=`echo "GET ${APACHE_STATUS_URL}?auto" | $NC_BIN -w $APACHE_STATUS_TIMEOUT $APACHE_HOST $APACHE_PORT`
if [ "$METRIC" = "TotalWorkers" ]; then
  BUSY=`echo "$DATA" | grep BusyWorkers | cut -d ':' -f2 | cut -d ' ' -f2`
  IDLE=`echo "$DATA" | grep IdleWorkers | cut -d ':' -f2 | cut -d ' ' -f2`
  if [ ! -z "$BUSY" ] && [ ! -z "$IDLE" ]; then
    echo $(( $BUSY + $IDLE ))
  fi
else
  echo "$DATA" | grep "$METRIC" | cut -d ':' -f2 | cut -d ' ' -f2
fi
