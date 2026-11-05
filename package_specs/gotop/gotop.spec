Name:       gotop
Version:    4.2.0
Release:    1
Summary:    A terminal based graphical activity monitor inspired by gtop and vtop
License:    AGPL-3.0-only
Source0:    %{name}_v%{version}_linux_amd64.tgz
Prefix:     /usr

%description
A terminal based graphical activity monitor inspired by gtop and vtop.

%prep
%setup -q -c %{name}-%{version}

%build

%install
rm -rf %{buildroot}
install -Dm755 gotop %{buildroot}%{_bindir}/gotop

%files
%{_bindir}/gotop

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.2.0-1
- Not in the r13.1 book; 4.2.0 is the latest maintained release
  (2026-11-05). The previous cjbassi/cdown repository is archived; the
  maintained fork is xxxserxxx/gotop.
- Follow the release asset naming (gotop_v4.2.0_linux_amd64.tgz) and
  install the binary in /usr/bin.

* Fri Jun 12 2020 Chris Statzer <chris.statzer@qq.com> 3.0.0
- Initial RPM
