Summary: MySQL zabbix template
Name: zabbix-quanta-mysql
Version: 1.0
Release: 1
License: GPL
Distribution: Quanta
Vendor: Quanta-Computing
Packager: Matthieu ROSINSKI <sysadmin@quanta-computing.com>
Source: zabbix-quanta-mysql.tar.gz
Requires: zabbix-agent >= 2.0
Requires: mysql-client

%description
This package provides a Zabbix MySQL template (userparameters) to add some MySQL metrics to Quanta.

%prep
rm -rf $RPM_BUILD_DIR/zabbix-quanta-mysql-*
zcat %{SOURCE0} | tar -xvf -

%build

%install
mkdir -pv $RPM_BUILD_ROOT/var/lib/zabbix/quanta
mkdir -pv $RPM_BUILD_ROOT/var/lib/zabbix/quanta/etc
mkdir -pv $RPM_BUILD_ROOT/etc/zabbix/zabbix-agentd.d/
cp -vr $RPM_BUILD_DIR/zabbix-quanta-mysql-1.0.1/scripts/bin/ $RPM_BUILD_ROOT/var/lib/zabbix/quanta/.
cp -v $RPM_BUILD_DIR/zabbix-quanta-mysql-1.0.1/dbconfig/quanta_mysql.rpm.conf $RPM_BUILD_ROOT/var/lib/zabbix/quanta/etc/quanta_mysql
cp -v $RPM_BUILD_DIR/zabbix-quanta-mysql-1.0.1/conf/quanta_mysql.conf $RPM_BUILD_ROOT/etc/zabbix/zabbix-agentd.d/quanta_mysql.conf

%files
%config /etc/zabbix/zabbix-agentd.d/quanta_mysql.conf
%config %attr(640,root,zabbix) /var/lib/zabbix/quanta/etc/quanta_mysql
/var/lib/zabbix/quanta/bin/quanta_mysql_status.sh
/var/lib/zabbix/quanta/bin/quanta_mysql_var.sh
