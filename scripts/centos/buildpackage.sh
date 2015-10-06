#!/bin/sh
# This script accepts a package name in parameter and copy the files to the appropriate
# locations. Files will be copied from $SRCPATH/$pkg-$version (version is auto-guessed)
# It then runs rpmbuild to build the package from the spec

if [ -z "$1" ]; then
  echo "Usage: buildpackage.sh <package> [package_dir]"
  exit 1
fi

if [ -z "$2" ]; then
  PKGD=/build/zabbix-quanta
else
  PKGD=$2
fi

SRCD=/root/rpmbuild/SOURCES
SPECD=/root/rpmbuild/SPECS

PKG=$1

PKGTAR=${SRCD}/$PKG.tar.gz
PKGNAME=`find ${PKGD} -type d -name ${PKG}-\* -printf "%f\n" | head -1`
PKGPATH=$PKGD/$PKGNAME

echo 'Creating TAR achive'
rm -vf $PKGTAR
tar -C $PKGD -czf $PKGTAR $PKGNAME

echo 'Copying spec file'
cp -vf $PKGPATH/$PKG.spec $SPECD

echo 'Building package'
rpmbuild -ba $SPECD/$PKG.spec
