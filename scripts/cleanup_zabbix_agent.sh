#!/bin/sh
dpkg --purge zabbix-quanta-mysql
echo PURGE | debconf-communicate zabbix-quanta-mysql
