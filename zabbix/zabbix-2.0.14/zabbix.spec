Name		: zabbix
Version		: 2.0.14
Release		: 3%{?dist}
Summary		: Enterprise-class open source distributed monitoring solution.
Distribution: Quanta
Vendor: Quanta-Computing
Packager: Matthieu ROSINSKI <sysadmin@quanta-computing.com>
Group		: Applications/Internet
License		: GPLv2+
URL		: http://www.zabbix.com/
Source0		: zabbix.tar.gz
Source4   : zabbix-agent.init
Patch0		: config.patch
Patch1		: fonts-config.patch

Buildroot	: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%define _unpackaged_files_terminate_build 0
%define _missing_doc_files_terminate_build 0

Requires	: logrotate
Requires(pre)	: /usr/sbin/useradd

%description
Zabbix is software that monitors numerous parameters of a network and
the health and integrity of servers. Zabbix uses a flexible
notification mechanism that allows users to configure e-mail based
alerts for virtually any event.  This allows a fast reaction to server
problems. Zabbix offers excellent reporting and data visualisation
features based on the stored data. This makes Zabbix ideal for
capacity planning.

Zabbix supports both polling and trapping. All Zabbix reports and
statistics, as well as configuration parameters are accessed through a
web-based front end. A web-based front end ensures that the status of
your network and the health of your servers can be assessed from any
location. Properly configured, Zabbix can play an important role in
monitoring IT infrastructure. This is equally true for small
organisations with a few servers and for large companies with a
multitude of servers.

%package agent
Summary		: Zabbix Agent
Group		: Applications/Internet
Requires	: zabbix = %{version}-%{release}
Requires(post)	: /sbin/chkconfig
Requires(preun)	: /sbin/chkconfig
Requires(preun)	: /sbin/service

%description agent
The Zabbix client agent, to be installed on monitored systems.

%prep
%setup0 -q -n %{name}-%{version}
%patch0 -p1
%patch1 -p1

# DejaVu fonts doesn't exist on EL <= 5
%if 0%{?fedora} || 0%{?rhel} >= 6
# remove included fonts
rm -rf frontends/php/fonts/DejaVuSans.ttf
%endif

# remove executable permissions
chmod a-x upgrades/dbpatches/1.8/mysql/upgrade

# fix up some lib64 issues
sed -i.orig -e 's|_LIBDIR=/usr/lib|_LIBDIR=%{_libdir}|g' \
    configure

# kill off .htaccess files, options set in SOURCE1
rm -f frontends/php/include/.htaccess
rm -f frontends/php/include/classes/.htaccess
rm -f frontends/php/api/.htaccess
rm -f frontends/php/conf/.htaccess

# set timestamp on modified config file and directories
touch -r frontends/php/css.css frontends/php/include/config.inc.php \
    frontends/php/include/defines.inc.php \
    frontends/php/include \
    frontends/php/include/classes

# fix path to traceroute utility
sed -i.orig -e 's|/usr/bin/traceroute|/bin/traceroute|' database/mysql/data.sql
sed -i.orig -e 's|/usr/bin/traceroute|/bin/traceroute|' database/postgresql/data.sql
sed -i.orig -e 's|/usr/bin/traceroute|/bin/traceroute|' database/sqlite3/data.sql

# remove .orig files in frontend
find frontends/php -name '*.orig'|xargs rm -f

# remove prebuild Windows binaries
rm -rf bin

# change log directory of zabbix_java.log
sed -i -e 's|/tmp/zabbix_java.log|/var/log/zabbix/zabbix_java_gateway.log|g' src/zabbix_java/lib/logback.xml

%build

%configure --enable-dependency-tracking --sysconfdir=/etc/zabbix --enable-agent
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

# install
make DESTDIR=$RPM_BUILD_ROOT install

# remove unnecessary files
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
rm -rf $RPM_BUILD_ROOT%{_datadir}/%{name}
find ./frontends/php -name '*.orig'|xargs rm -f
find ./database -name '*.orig'|xargs rm -f

# set up some required directories
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/web
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/init.d
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
mkdir -p $RPM_BUILD_ROOT/usr/lib/%{name}/alertscripts
mkdir -p $RPM_BUILD_ROOT/usr/lib/%{name}/externalscripts
mkdir -p $RPM_BUILD_ROOT%{_datadir}
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/run/%{name}
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/quanta

# install zabbix_agent.conf and userparameter files
install -dm 755 $RPM_BUILD_ROOT%{_docdir}/%{name}-agent-%{version}
install -m 0644 conf/zabbix_agent.conf $RPM_BUILD_ROOT%{_docdir}/%{name}-agent-%{version}
install -dm 755 $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/zabbix_agentd.d
install -m 755 scripts/quanta_zabbix_setup.sh $RPM_BUILD_ROOT%{_bindir}/quanta_zabbix_setup

# fix config file options
cat conf/zabbix_agentd.conf | sed \
    -e '/^# PidFile=/a \\nPidFile=%{_localstatedir}/run/zabbix/zabbix_agentd.pid' \
    -e 's|^LogFile=.*|LogFile=%{_localstatedir}/log/%{name}/zabbix_agentd.log|g' \
    -e 's/^ServerActive=.*/ServerActive=zabbix-20-1.quanta-computing.com/g' \
    -e 's/^Server=.*/Server=62.4.6.33,62.4.6.34,62.4.6.35,62.4.6.36,62.4.6.37,62.4.6.38,62.4.6.39,62.4.6.40,62.4.6.41,62.4.6.42,62.4.6.43,62.4.6.44,62.4.6.45,62.4.6.46,62.4.6.47,62.4.6.48,62.4.6.49,62.4.6.50,62.4.6.51,62.4.6.52,62.4.6.53,62.4.6.54,62.4.6.55,62.4.6.56,62.4.6.57,62.4.6.58,62.4.6.59,62.4.6.60,62.4.6.61,62.4.6.62,62.4.6.63/g' \
    -e 's/^Hostname=.*//g' \
    -e '/^# LogFileSize=.*/a \\nLogFileSize=0' \
    -e '/^# Include=$/a \\nInclude=%{_sysconfdir}/%{name}/zabbix_agentd.d/' \
    > $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/zabbix_agentd.conf

# install log rotation
cat %{SOURCE2} | sed -e 's|COMPONENT|agentd|g' > \
     $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/zabbix-agent

# init scripts
install -m 0755 -p %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/init.d/zabbix-agent

# nuke static libs and empty oracle upgrade sql
rm -rf $RPM_BUILD_ROOT%{_libdir}/libzbx*.a

# remove extraneous ones
rm -rf $RPM_BUILD_ROOT%{_datadir}/%{name}/create


%clean
rm -rf $RPM_BUILD_ROOT


%pre
getent group zabbix > /dev/null || groupadd -r zabbix
getent passwd zabbix > /dev/null || \
    useradd -r -g zabbix -d %{_localstatedir}/lib/zabbix -s /sbin/nologin \
    -c "Zabbix Monitoring System" zabbix
:

%post agent
/sbin/chkconfig --add zabbix-agent || :

%preun agent
if [ "$1" = 0 ]
then
  /sbin/service zabbix-agent stop >/dev/null 2>&1
  /sbin/chkconfig --del zabbix-agent
fi
:

%postun agent
if [ $1 -ge 1 ]
then
  /sbin/service zabbix-agent try-restart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README
%dir %{_sysconfdir}/zabbix
%attr(0755,zabbix,zabbix) %dir %{_localstatedir}/log/zabbix
%attr(0755,zabbix,zabbix) %dir %{_localstatedir}/run/zabbix
%attr(0755,zabbix,zabbix) %dir %{_localstatedir}/lib/zabbix/quanta


%files agent
%defattr(-,root,root,-)
%{_docdir}/%{name}-agent-%{version}/
%config(noreplace) %{_sysconfdir}/zabbix/zabbix_agentd.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/zabbix-agent
%dir %{_sysconfdir}/zabbix/zabbix_agentd.d
%{_sysconfdir}/init.d/zabbix-agent
%{_sbindir}/zabbix_agent
%{_sbindir}/zabbix_agentd
%{_mandir}/man8/zabbix_agentd.8*
%{_bindir}/quanta_zabbix_setup


%changelog
* Tue Dec 16 2014 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.14-1
- update to 2.0.14
- fix status parameter of init scripts

* Mon Sep 22 2014 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.13-1
- update to 2.0.13

* Sat May 17 2014 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.12-1
- update to 2.0.12

* Sat Feb 15 2014 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.11-1
- update to 2.0.11
- change lockfile name to zabbix-server

* Thu Dec 12 2013 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.10-1
- update to 2.0.10

* Sat Oct 12 2013 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.9-1
- update to 2.0.9
- remove cve-2013-5743 patch

* Thu Oct 3 2013 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.8-3
- fix cve-2013-5743 patch was not applied

* Sat Sep 28 2013 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.8-2
- fix CVE-2013-5743

* Sun Aug 25 2013 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.8-1
- update to 2.0.8

* Thu Aug 1 2013 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.7-1
- update to 2.0.7

* Tue Apr 23 2013 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.6-1
- update to 2.0.6
- fix zabbix-java-gateway init script

* Wed Feb 13 2013 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.5-1
- update to 2.0.5

* Sun Dec 9 2012 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.4-1
- update to 2.0.4

* Tue Oct 16 2012 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.3-1
- update to 2.0.3


* Wed Aug 1 2012 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.2-1
- update to 2.0.2

* Mon Jul 16 2012 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.1-2
- move userparameter_examples.conf to docdir
- move java gateway log file to /var/log/zabbix

* Tue Jul 3 2012 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.1-1
- update to 2.0.1

* Wed May 30 2012 Kodai Terashima <kodai.terashima@zabbix.com> - 2.0.0-1
- update to 2.0.0

* Wed Apr 25 2012 Kodai Terashima <kodai.terashima@zabbix.com> -1.8.12-1
- update to 1.8.12

* Tue Apr 3 2012 Kodai Terashima <kodai.terashima@zabbix.com> - 1.8.11-1
- update to 1.8.11
- move maintenance.inc.php to /etc/zabbix/web

* Wed Feb 8 2012 Kodai Terashima <kodai.terashima@zabbix.com> - 1.8.10-1
- update to 1.8.10
- remove snmptrap related files
- move init scripts to zabbix source
- separate get and sender subpackages
- remove server-sqlite3 and web-sqlite3 subpackages
- add web-japanese subpackage
- move alertscripts and externalscripts to /usr/lib/zabbix
- improve default parameter of config files
- delete dependency for zabbix from web package
- move zabbix_agent.conf to docdir

* Tue Aug  9 2011 Dan Horák <dan[at]danny.cz> - 1.8.6-1
- updated to 1.8.6 (#729164, #729165)
- updated user/group adding scriptlet

* Mon May 23 2011 Dan Horák <dan[at]danny.cz> - 1.8.5-2
- include /var/lib/zabbix and /etc/zabbix/externalscripts dirs in package (#704181)
- add snmp trap receiver script in package (#705331)

* Wed Apr 20 2011 Dan Horák <dan[at]danny.cz> - 1.8.5-1
- updated to 1.8.5

* Tue Jan 18 2011 Dan Horák <dan[at]danny.cz> - 1.8.4-2
- enable libcurl detection (#670500)

* Tue Jan  4 2011 Dan Horák <dan[at]danny.cz> - 1.8.4-1
- updated to 1.8.4
- fixes zabbix_agent fail to start on IPv4-only host (#664639)

* Tue Nov 23 2010 Dan Horák <dan[at]danny.cz> - 1.8.3-3
- zabbix emailer doesn't handle multiline responses (#656072)

* Tue Oct 05 2010 jkeating - 1.8.3-2.1
- Rebuilt for gcc bug 634757

* Mon Sep  6 2010 Dan Horák <dan[at]danny.cz> - 1.8.3-2
- fix font path in patch2 (#630500)

* Tue Aug 17 2010 Dan Horák <dan[at]danny.cz> - 1.8.3-1
- updated to 1.8.3

* Wed Aug 11 2010 Dan Horák <dan[at]danny.cz> - 1.8.2-3
- added patch for XSS in triggers page (#620809, ZBX-2326)

* Thu Apr 29 2010 Dan Horák <dan[at]danny.cz> - 1.8.2-2
- DejaVu fonts doesn't exist on EL <= 5

* Tue Mar 30 2010 Dan Horák <dan[at]danny.cz> - 1.8.2-1
- Update to 1.8.2

* Sat Mar 20 2010 Dan Horák <dan[at]danny.cz> - 1.8.1-7
- web interface needs php-xml (#572413)
- updated defaults in config files (#573325)
- built with libssh2 support (#575279)

* Wed Feb 24 2010 Dan Horák <dan[at]danny.cz> - 1.8.1-6
- use system fonts

* Mon Feb  1 2010 Dan Horák <dan[at]danny.cz> - 1.8.1-4
- enable dependency tracking

* Mon Feb  1 2010 Dan Horák <dan[at]danny.cz> - 1.8.1-3
- updated the web-config patch

* Mon Feb  1 2010 Dan Horák <dan[at]danny.cz> - 1.8.1-2
- close fd on exec (#559221)

* Fri Jan 29 2010 Dan Horák <dan[at]danny.cz> - 1.8.1-1
- Update to 1.8.1

* Tue Jan 26 2010 Dan Horák <dan[at]danny.cz> - 1.8-1
- Update to 1.8

* Thu Dec 31 2009 Dan Horák <dan[at]danny.cz> - 1.6.8-1
- Update to 1.6.8
- Upstream changelog: http://www.zabbix.com/rn1.6.8.php
- fixes 2 issues from #551331

* Wed Nov 25 2009 Dan Horák <dan[at]danny.cz> - 1.6.6-2
- rebuilt with net-snmp 5.5

* Sat Aug 29 2009 Dan Horák <dan[at]danny.cz> - 1.6.6-1
- Update to 1.6.6
- Upstream changelog: http://www.zabbix.com/rn1.6.6.php

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 1.6.5-3
- rebuilt with new openssl

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jun  8 2009 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.6.5-1
- Update to 1.6.5, see http://sourceforge.net/mailarchive/message.php?msg_name=4A37A2CA.8050503%40zabbix.com for the full release notes.
-
- It is recommended to create the following indexes in order to speed up
- performance of ZABBIX front-end as well as server side (ignore it if the
- indexes already exist):
-
- CREATE UNIQUE INDEX history_log_2 on history_log (itemid,id);
- CREATE UNIQUE INDEX history_text_2 on history_text (itemid,id);
- CREATE INDEX graphs_items_1 on graphs_items (itemid);
- CREATE INDEX graphs_items_2 on graphs_items (graphid);
- CREATE INDEX services_1 on services (triggerid);

* Mon Jun  8 2009 Ville Skyttä <ville.skytta at iki.fi> - 1.6.4-4
- Start agent after and shut down before proxy and server by default.
- Include database schemas also in -proxy-* docs.
- Make buildable on EL-4 (without libcurl, OpenIPMI).
- Reformat description.

* Fri Apr 17 2009 Ville Skyttä <ville.skytta at iki.fi> - 1.6.4-3
- Tighten configuration file permissions.
- Ensure zero exit status from scriptlets.
- Improve init script LSB compliance.
- Restart running services on package upgrades.

* Thu Apr  9 2009 Dan Horák <dan[at]danny.cz> - 1.6.4-2
- make the -docs subpackage noarch

* Thu Apr  9 2009 Dan Horák <dan[at]danny.cz> - 1.6.4-1
- update to 1.6.4
- remove the cpustat patch, it was integreated into upstream
- use noarch subpackage for the web interface
- database specific web subpackages conflicts with each other
- use common set of option for the configure macro
- enable IPMI support
- sqlite web subpackage must depend on local sqlite
- reorganize the docs and the sql scripts
- change how the web interface config file is created
- updated scriptlet for adding the zabbix user
- move the documentation in PDF to -docs subpackage
- most of the changes were submitted by Ville Skyttä in #494706
- Resolves: #489673, #493234, #494706

* Mon Mar  9 2009 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.6.2-5
- Update pre patch due to incomplete fix for security problems.

* Wed Mar  4 2009 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.6.2-4
- Update to a SVN snapshot of the upstream 1.6 branch to fix security
  issue (BZ#488501)

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Jan 23 2009 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.6.2-2
- Rebuild for MySQL 5.1.X

* Fri Jan 16 2009 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.6.2-1
- Update to 1.6.2: http://www.zabbix.com/rn1.6.2.php

* Thu Dec  4 2008 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.6.1-1
- Fix BZ#474593 by adding a requires.

* Wed Nov  5 2008 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.6.1-1
- Update to 1.6.1

* Tue Sep 30 2008 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.6-1.1
- Bump release because forgot to add some new files.

* Mon Aug 11 2008 Jason L Tibbitts III <tibbs@math.uh.edu> - 1.4.6-2
- Fix license tag.

* Fri Jul 25 2008 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.4.6-1
- Update to 1.4.6

* Mon Jul 07 2008 Dan Horak <dan[at]danny.cz> - 1.4.5-4
- add LSB headers into init scripts
- disable internal log rotation

* Fri May 02 2008 Jarod Wilson <jwilson@redhat.com> - 1.4.5-3
- Seems the zabbix folks replaced the original 1.4.5 tarball with
  an updated tarball or something -- it actually does contain a
  tiny bit of additional code... So update to newer 1.4.5.

* Tue Apr 08 2008 Jarod Wilson <jwilson@redhat.com> - 1.4.5-2
- Fix building w/postgresql (#441456)

* Tue Mar 25 2008 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.4.5-1
- Update to 1.4.5

* Thu Feb 14 2008 Jarod Wilson <jwilson@redhat.com> - 1.4.4-2
- Bump and rebuild with gcc 4.3

* Mon Dec 17 2007 Jarod Wilson <jwilson@redhat.com> - 1.4.4-1
- New upstream release
- Fixes two crasher bugs in 1.4.3 release

* Wed Dec 12 2007 Jarod Wilson <jwilson@redhat.com> - 1.4.3-1
- New upstream release

* Thu Dec 06 2007 Release Engineering <rel-eng at fedoraproject dot org> - 1.4.2-5
- Rebuild for deps

* Sat Dec 01 2007 Dan Horak <dan[at]danny.cz> 1.4.2-4
- add security fix (#407181)

* Thu Sep 20 2007 Dan Horak <dan[at]danny.cz> 1.4.2-3
- Add a patch to clean a warning during compile
- Add a patch to fix cpu load computations

* Tue Aug 21 2007 Jarod Wilson <jwilson@redhat.com> 1.4.2-2
- Account for binaries moving from %%_bindir to %%_sbindir

* Tue Aug 21 2007 Jarod Wilson <jwilson@redhat.com> 1.4.2-1
- New upstream release

* Mon Jul 02 2007 Jarod Wilson <jwilson@redhat.com> 1.4.1-1
- New upstream release

* Fri Jun 29 2007 Jarod Wilson <jwilson@redhat.com> 1.4-3
- Install correct sql init files (#244991)
- Add Requires: php-bcmath to zabbix-web (#245767)

* Wed May 30 2007 Jarod Wilson <jwilson@redhat.com> 1.4-2
- Add placeholder zabbix.conf.php

* Tue May 29 2007 Jarod Wilson <jwilson@redhat.com> 1.4-1
- New upstream release

* Fri Mar 30 2007 Jarod Wilson <jwilson@redhat.com> 1.1.7-1
- New upstream release

* Wed Feb 07 2007 Jarod Wilson <jwilson@redhat.com> 1.1.6-1
- New upstream release

* Thu Feb 01 2007 Jarod Wilson <jwilson@redhat.com> 1.1.5-1
- New upstream release

* Tue Jan 02 2007 Jarod Wilson <jwilson@redhat.com> 1.1.4-5
- Add explicit R:php to zabbix-web (#220676)

* Wed Dec 13 2006 Jarod Wilson <jwilson@redhat.com> 1.1.4-4
- Fix snmp polling buffer overflow (#218065)

* Wed Nov 29 2006 Jarod Wilson <jwilson@redhat.com> 1.1.4-3
- Rebuild for updated libnetsnmp

* Thu Nov 16 2006 Jarod Wilson <jwilson@redhat.com> 1.1.4-2
- Fix up pt_br
- Add Req-pre on useradd

* Wed Nov 15 2006 Jarod Wilson <jwilson@redhat.com> 1.1.4-1
- Update to 1.1.4

* Tue Nov 14 2006 Jarod Wilson <jwilson@redhat.com> 1.1.3-3
- Add BR: gnutls-devel, R: net-snmp-libs

* Tue Nov 14 2006 Jarod Wilson <jwilson@redhat.com> 1.1.3-2
- Fix php-pgsql Requires

* Tue Nov 14 2006 Jarod Wilson <jwilson@redhat.com> 1.1.3-1
- Update to 1.1.3

* Mon Oct 02 2006 Jarod Wilson <jwilson@redhat.com> 1.1.2-1
- Update to 1.1.2
- Enable alternate building with postgresql support

* Thu Aug 17 2006 Jarod Wilson <jwilson@redhat.com> 1.1.1-2
- Yank out Requires: mysql-server
- Add Requires: for php-gd and fping

* Tue Aug 15 2006 Jarod Wilson <jwilson@redhat.com> 1.1.1-1
- Update to 1.1.1
- More macroification
- Fix up zabbix-web Requires:
- Prep for enabling postgres support

* Thu Jul 27 2006 Jarod Wilson <jwilson@redhat.com> 1.1-2
- Add Requires: on chkconfig and service
- Remove openssl-devel from BR, mysql-devel pulls it in
- Alter scriptlets to match Fedora conventions

* Tue Jul 11 2006 Jarod Wilson <jwilson@redhat.com> 1.1-1
- Initial build for Fedora Extras
