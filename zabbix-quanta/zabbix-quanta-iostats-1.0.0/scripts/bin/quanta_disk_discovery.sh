#!/bin/sh
#
# This script discovers installed hard drives and format an output suitable
# for zabbix discovery rules
#
# Usage: quanta_disk_discovery.sh
#

echo -n '{"data":['
first=0
for disk in `grep -E '[sh]d[a-z]$' /proc/partitions | awk '{print $4}'`; do
  if [ $first -eq 0 ]; then
    first=1
  else
    echo -n ","
  fi
  ssize=0
  if [ -f "/sys/block/$disk/queue/hw_sector_size" ]; then
    ssize=`cat /sys/block/$disk/queue/hw_sector_size`
  fi
  echo -n "{\"{#DISKNAME}\":\"$disk\",\"{#SECTORSIZE}\":$ssize}";
done
echo ']}'
