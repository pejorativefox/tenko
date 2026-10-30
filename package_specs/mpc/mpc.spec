Name:       mpc
Version:    1.4.1
Release:    1
Summary:    TODO
License:    GPL3
Source0:    mpc-1.4.1.tar.xz
Prefix:     /usr

%description
TODO

%prep
%setup -q

%build
%configure --disable-static --docdir=/usr/share/doc/mpc-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/include/mpc.h
/usr/lib64/libmpc.so
/usr/lib64/libmpc.so.3
/usr/lib64/libmpc.so.3.4.1
/usr/lib64/pkgconfig/mpc.pc
/usr/share/info/mpc.info.gz

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.4.1
- Sync with LFS r13.1

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 1.3.1
- Version bump
