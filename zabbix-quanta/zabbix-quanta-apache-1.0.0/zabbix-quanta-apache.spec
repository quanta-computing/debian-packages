Summary: Apache zabbix template
Name: zabbix-quanta-apache
Version: 1.0
Release: 1
License: GPL
Distribution: Quanta
Vendor: Quanta-Computing
Packager: Matthieu ROSINSKI <sysadmin@quanta-computing.com>
Source: zabbix-quanta-apache.tar.gz
Requires: zabbix-agent >= 2.0
Requires: netcat >= 1.10

%description
This package provides a Zabbix Apache template (userparameters) to add Apache metrics to Quanta.

%prep
rm -rf $RPM_BUILD_DIR/zabbix-quanta-apache-*
zcat %{SOURCE0} | tar -xvf -

%build

%install
mkdir -pv $RPM_BUILD_ROOT/var/lib/zabbix/quanta
mkdir -pv $RPM_BUILD_ROOT/etc/zabbix/zabbix-agentd.d/
cp -vr $RPM_BUILD_DIR/zabbix-quanta-apache-1.0.0/scripts/bin/ $RPM_BUILD_ROOT/var/lib/zabbix/quanta/.
cp -vr $RPM_BUILD_DIR/zabbix-quanta-apache-1.0.0/scripts/etc/ $RPM_BUILD_ROOT/var/lib/zabbix/quanta/.
cp -v $RPM_BUILD_DIR/zabbix-quanta-apache-1.0.0/conf/quanta_apache.conf $RPM_BUILD_ROOT/etc/zabbix/zabbix-agentd.d/quanta_apache.conf

%files
%config /etc/zabbix/zabbix-agentd.d/quanta_apache.conf
%config /var/lib/zabbix/quanta/etc/quanta_apache
/var/lib/zabbix/quanta/bin/quanta_apache.sh
