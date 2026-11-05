Name:       pm-utils
Version:    1.4.1
Release:    1
Summary:    Power Management Utilities
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.gz
Source1:    %{name}-%{version}-bugfixes-1.patch
Prefix:     /usr

%description
The Power Management Utilities provide simple shell command line tools to suspend and hibernate the computer. They can be used to run user supplied scripts on suspend and resume.

%prep
%setup -q
patch -Np1 -i %{SOURCE1}

%build
./configure --prefix=/usr                          \
            --sysconfdir=/etc                      \
            --docdir=/usr/share/doc/pm-utils-%{version} \
            --disable-docs
%make_build

%install
rm -rf %{buildroot}
%make_install

# xmlto is not part of the base image, so install the pregenerated man
# pages exactly as the r13.1 book does.
install -d %{buildroot}%{_mandir}/man1 %{buildroot}%{_mandir}/man8
install -v -m644 man/*.1 %{buildroot}%{_mandir}/man1/
install -v -m644 man/*.8 %{buildroot}%{_mandir}/man8/
ln -sv pm-action.8 %{buildroot}%{_mandir}/man8/pm-suspend.8
ln -sv pm-action.8 %{buildroot}%{_mandir}/man8/pm-hibernate.8
ln -sv pm-action.8 %{buildroot}%{_mandir}/man8/pm-suspend-hybrid.8

%files
/usr/bin/on_ac_power
/usr/bin/pm-is-supported
/usr/lib/pkgconfig/pm-utils.pc
/usr/lib/pm-utils/bin/pm-action
/usr/lib/pm-utils/bin/pm-pmu
/usr/lib/pm-utils/bin/pm-reset-swap
/usr/lib/pm-utils/bin/service
/usr/lib/pm-utils/defaults
/usr/lib/pm-utils/functions
/usr/lib/pm-utils/module.d/kernel
/usr/lib/pm-utils/module.d/tuxonice
/usr/lib/pm-utils/module.d/uswsusp
/usr/lib/pm-utils/pm-functions
/usr/lib/pm-utils/power.d/disable_wol
/usr/lib/pm-utils/power.d/hal-cd-polling
/usr/lib/pm-utils/power.d/harddrive
/usr/lib/pm-utils/power.d/intel-audio-powersave
/usr/lib/pm-utils/power.d/journal-commit
/usr/lib/pm-utils/power.d/laptop-mode
/usr/lib/pm-utils/power.d/pcie_aspm
/usr/lib/pm-utils/power.d/readahead
/usr/lib/pm-utils/power.d/sata_alpm
/usr/lib/pm-utils/power.d/sched-powersave
/usr/lib/pm-utils/power.d/wireless
/usr/lib/pm-utils/power.d/xfs_buffer
/usr/lib/pm-utils/sleep.d/00logging
/usr/lib/pm-utils/sleep.d/00powersave
/usr/lib/pm-utils/sleep.d/01grub
/usr/lib/pm-utils/sleep.d/49bluetooth
/usr/lib/pm-utils/sleep.d/55NetworkManager
/usr/lib/pm-utils/sleep.d/75modules
/usr/lib/pm-utils/sleep.d/90clock
/usr/lib/pm-utils/sleep.d/94cpufreq
/usr/lib/pm-utils/sleep.d/95led
/usr/lib/pm-utils/sleep.d/98video-quirk-db-handler
/usr/lib/pm-utils/sleep.d/99video
/usr/sbin/pm-hibernate
/usr/sbin/pm-powersave
/usr/sbin/pm-suspend
/usr/sbin/pm-suspend-hybrid
/usr/share/doc/pm-utils-1.4.1/HOWTO.hooks
/usr/share/doc/pm-utils-1.4.1/HOWTO.modules
/usr/share/doc/pm-utils-1.4.1/README
/usr/share/doc/pm-utils-1.4.1/README.debugging
/usr/share/doc/pm-utils-1.4.1/README.distributions
/usr/share/man/man1/*
/usr/share/man/man8/*

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.4.1-1
- BLFS r13.1 general/sysutils/pm-utils.xml (version 1.4.1).
- Apply the book's pm-utils-1.4.1-bugfixes-1.patch.
- Build without xmlto (--disable-docs) and install the pregenerated man
  pages the way the book does.
- Follow the book's unversioned libdir layout (/usr/lib) and versioned
  docdir; refresh %files from the actual install.

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 1.4.1
- Initial RPM
