# Dockerfile to use the package manager
# See README.md for more info
#

FROM debian:wheezy
MAINTAINER Matthieu ROSINSKI <korrigan@quanta-computing.com>

ENV DEBMAIL="sysadmin@quanta-computing.com"
ENV DEBFULLNAME="Quanta Computing"

RUN apt-get update && apt-get -y install \
  build-essential \
  debhelper \
  devscripts \
  dput \
  vim \
  quilt \
  wget
