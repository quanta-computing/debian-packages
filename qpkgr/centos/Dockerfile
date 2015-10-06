# Dockerfile to use the package manager
# See README.md for more info
#

FROM centos
MAINTAINER Matthieu ROSINSKI <korrigan@quanta-computing.com>

RUN yum install -y vim \
  rpmlint \
  rpm-build \
  rpmdevtools \
  redhat-rpm-config \
  make \
  gcc

RUN rpmdev-setuptree
