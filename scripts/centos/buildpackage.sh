#!/bin/sh
# This script accepts a package name in parameter and copy the files to the appropriate
# locations. Files will be copied from $SRCPATH/$pkg-$version (version is auto-guessed)
# It then runs rpmbuild to build the package from the spec

if [ -z "$1" ]; then
  echo "Usage: buildpackage.sh <package>"
  exit 1
fi

PKGD=/build/zabbix-quanta/
PKG=$1

PKGPATH=`find ${PKGD} -name '${PKG}-*' | head -1`
echo $PKGPATH
