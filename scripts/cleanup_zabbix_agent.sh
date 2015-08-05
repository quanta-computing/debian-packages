#!/bin/sh
dpkg --purge zabbix-agent
echo PURGE | debconf-communicate zabbix-agent
