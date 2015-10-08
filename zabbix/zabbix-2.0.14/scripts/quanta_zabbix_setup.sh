#!/bin/sh
#
# Script to auto-configure zabbix plugins for Quanta and to auto-register the agent
# to the app
# This script will try to register the agent to quanta if /etc/zabbix/quanta.token is empty.
# This script will try to configure Mysql is /var/lib/zabbix/quanta/etc/quanta_mysql is present and the
# values are empty
#
# Copyright Quanta Computing 2015
#
# Usage: quanta_zabbix_setup
#

# Utils
yesno() {
  case $1 in
    y*)
      echo -n "y"
      ;;
    Y*)
      echo -n "y"
      ;;
    n*)
      echo -n ""
      ;;
    N*)
      echo -n ""
      ;;
    *)
      echo -n $2
      ;;
  esac
}


QUANTA_TOKEN_FILE=/var/lib/zabbix/quanta/etc/quanta.token
QUANTA_MYSQL_CONFIG=/var/lib/zabbix/quanta/etc/quanta_mysql

# Autoregistration messages
IP_ADDR_MSG="Enter the public IP address on which zabbix-agent is reachable on this server"
TOKEN_MSG="Enter your Quanta autoregistration token, you can retrieve it your site settings in Quanta"
MODE_MSG="Please chose your polling mode: \n\
 - passive (recommended): our servers will connect to zabbox-agent\n\
 - active (your agent will connect to our servers)\n\
Enter your zabbix mode (default passive): "
WEB_MSG="Does this server hosts a webserver ? (y/N): "
DB_MSG="Does this servers hosts a database server ? (y/N): "

# MySQL config messages
MYSQL_USER_MSG="Enter the username of the new MySQL user (default zabbix-quanta): "
MYSQL_PASS_MSG="Enter the password of the new MySQL user (default to a random password): "
MYSQL_ROOT_PASS_MSG="Enter the password of the MySQL root user (won't be saved): "

# Autoregister agent if token is not present
if [ ! -f $QUANTA_TOKEN_FILE ]; then
  echo -n "Would you like to autoregister your server to Quanta ? (Y/n): "
  read AUTOREGISTER
  AUTOREGISTER=$(yesno $AUTOREGISTER y)
fi

if [ -z "$AUTOREGISTER" ]; then
  echo "Zabbix-agent was already registered with Quanta"
else
  # Get name
  NAME=`hostname`
  # Get public IP address
  IP=`/bin/hostname -I | cut -d ' ' -f 1`
  if [ -z $IP ] || echo "$IP" \
  | grep -E '(^127\.)|(^192\.168\.)|(^10\.)|(^172\.1[6-9]\.)|(^172\.2[0-9]\.)|(^172\.3[0-1]\.)|(^::1$)|(^[fF][cCdD])' > /dev/null
  then
    echo -n "$IP_ADDR_MSG: "
  else
    echo -n "$IP_ADDR_MSG (default $IP): "
  fi
  read HOST
  if [ -z "$HOST" ] && [ ! -z "$IP" ]; then
    HOST=$IP
  fi

  # Get token
  echo -n "$TOKEN_MSG: "
  read TOKEN

  # Get mode
  echo -n -e $MODE_MSG
  read MODE
  if [ -z "$MODE" ]; then
    MODE=passive
  fi


  # Get roles
  ROLE=""
  echo -n $WEB_MSG
  read ROLE_WEB
  ROLE_WEB=$(yesno $ROLE_WEB)
  echo -n $DB_MSG
  read ROLE_DB
  ROLE_DB=$(yesno $ROLE_DB)

  if [ ! -z $ROLE_WEB ] && [ ! -z $ROLE_DB ]; then
    ROLE=global
  elif [ ! -z $ROLE_WEB ]; then
    ROLE=front
  elif [ ! -z $ROLE_DB ]; then
    ROLE=database
  else
    ROLE=unknown
  fi

  # Register server
  DATA="{\"server\": {\"name\": \"$NAME\", \"host\": \"$HOST\", \"role\": \"$ROLE\", \"enabled\": true, \"template\": \"$MODE\"}}"
  QUANTA_URL="https://www.quanta-monitoring.com/api/system/autoregister/$TOKEN"
  if curl -s -m 30 -w '%{http_code}' -H 'Content-Type: application/json' -X POST --data "$DATA" $QUANTA_URL -o /dev/null 2>&1 \
  | grep 200 >/dev/null
  then
    echo $TOKEN > $QUANTA_TOKEN_FILE
    echo "Registered $NAME on Quanta, please check if everything is OK in Quanta (settings -> system)" >&2
  else
    echo "Uh oh... An error occured while auto-registering zabbix-agent to Quanta, please configure it manually" >&2
  fi

fi

# Configure mysql if the values are empty in /var/lib/zabbix/quanta/etc/quanta_mysql
if [ -f $QUANTA_MYSQL_CONFIG ]; then
  . $QUANTA_MYSQL_CONFIG
  if [ -z "$MYSQL_USER" ] || [ -z "$MYSQL_PASSWORD" ]; then
    echo -n "Quanta-MySQL plugin is not configured, would you like to do it now ? (Y/n): "
    read CONFIG_MYSQL
    CONFIG_MYSQL=$(yesno $CONFIG_MYSQL y)
    if [ -z $CONFIG_MYSQL ]; then
      exit 0
    fi

    echo -n $MYSQL_USER_MSG
    read MYSQL_USER
    if [ -z "$MYSQL_USER" ]; then
      MYSQL_USER=zabbix-quanta
    fi
    echo -n $MYSQL_PASS_MSG
    read -s MYSQL_PASSWORD
    echo
    if [ -z $MYSQL_PASSWORD ]; then
      MYSQL_PASSWORD=`</dev/urandom tr -dc '[:alnum:]' | head -c 10`
    fi
    echo -n $MYSQL_ROOT_PASS_MSG
    read -s MYSQL_ROOT_PASSWORD
    echo
    if [ -z "$MYSQL_ROOT_PASSWORD" ]; then
      PASSWORD_ARGS=""
    else
      PASSWORD_ARGS="--password=''$MYSQL_ROOT_PASSWORD'"
    fi
    echo "CREATE USER '$MYSQL_USER'@localhost IDENTIFIED BY '$MYSQL_PASSWORD';" | mysql --user=root $PASSWORD_ARGS
    if [ $? -eq 0 ]; then
      sed -i -e "s/MYSQL_USER=.*/MYSQL_USER='$MYSQL_USER'/" $QUANTA_MYSQL_CONFIG
      sed -i -e "s/MYSQL_PASSWORD=.*/MYSQL_PASSWORD='$MYSQL_PASSWORD'/" $QUANTA_MYSQL_CONFIG
      echo "Quanta-MySQL plugin successfully configured"
    else
      echo "Oops, an error occured"
    fi
  else
    echo "Quanta-MySQL plugin for zabbix is already configured"
  fi
fi
