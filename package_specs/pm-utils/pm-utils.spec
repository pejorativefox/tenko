Name:       pm-utils
Version:    1.4.1
Release:    1
Summary:    Power Management Utilities
License:    GPL-2.0-or-later
URL:        https://pm-utils.freedesktop.org/wiki/
Source0:    %{name}-%{version}.tar.gz
Patch0:     %{name}-%{version}-bugfixes-1.patch
Prefix:     /usr

%description
The Power Management Utilities provide simple shell command line tools to suspend and hibernate the computer. They can be used to run user supplied scripts on suspend and resume.

%prep
%setup -q
%patch -P 0 -p1

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
# pages exactly as the base build does.
install -d %{buildroot}%{_mandir}/man1 %{buildroot}%{_mandir}/man8
install -v -m644 man/*.1 %{buildroot}%{_mandir}/man1/
install -v -m644 man/*.8 %{buildroot}%{_mandir}/man8/
ln -sv pm-action.8 %{buildroot}%{_mandir}/man8/pm-suspend.8
ln -sv pm-action.8 %{buildroot}%{_mandir}/man8/pm-hibernate.8
ln -sv pm-action.8 %{buildroot}%{_mandir}/man8/pm-suspend-hybrid.8

%files -f %{_sourcedir}/pm-utils.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.4.1-1
- Basis: tenko.lock (pm-utils 1.4.1).
- Apply the documented pm-utils-1.4.1-bugfixes-1.patch.
- Build without xmlto (--disable-docs) and install the pregenerated man
  pages the way the base build does.
- Follow the documented unversioned libdir layout (/usr/lib) and versioned
  docdir; refresh %files from the actual install.

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 1.4.1
- Initial RPM
