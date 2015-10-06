Summary: IOstat zabbix template
Name: zabbix-quanta-iostats
Version: 1.0
Release: 1
License: GPL
Distribution: Quanta
Vendor: Quanta-Computing
Packager: Matthieu ROSINSKI <sysadmin@quanta-computing.com>
Source: zabbix-quanta-iostats_1.0.0.tar.gz

%description
This package provides a Zabbix IOstat template (userparameters) for use
with Quanta.

%prep
rm -rf $RPM_BUILD_DIR/zabbix-quanta-iostats-1.0
zcat %{SOURCE0} | tar -xvf -

%build

%install
mkdir -pv $RPM_BUILD_ROOT/var/lib/zabbix/quanta
mkdir -pv $RPM_BUILD_ROOT/etc/zabbix/zabbix-agentd.d/
cp -vr $RPM_BUILD_DIR/zabbix-quanta-iostats-1.0.0/scripts/bin/ $RPM_BUILD_ROOT/var/lib/zabbix/quanta/.
cp -v $RPM_BUILD_DIR/zabbix-quanta-iostats-1.0.0/conf/quanta_iostsats.conf $RPM_BUILD_ROOT/etc/zabbix/zabbix-agentd.d/quanta_iostats.conf

%files
%config /etc/zabbix/zabbix-agentd.d/quanta_iostats.conf
/var/lib/zabbix/quanta/bin/quanta_disk_discovery.sh
