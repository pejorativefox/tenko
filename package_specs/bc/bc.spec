Name:       bc
Version:    7.0.3
Release:    1
Summary:    Bc, an arbitrary precision numeric processing language. 
License:    GPL3
Source0:    bc-7.0.3.tar.xz
Prefix:     /usr

%description
TODO

%prep
%setup -q

%build
CC='gcc -std=c99' ./configure --prefix=/usr -G -O3 -r
%make_build

%install
rm -rf %{buildroot}
make install_locales DESTDIR=%{buildroot}
install -Dm755 bin/bc %{buildroot}%{_bindir}/bc
install -Dm755 bin/dc %{buildroot}%{_bindir}/dc
install -Dm644 manuals/bc.1 %{buildroot}%{_mandir}/man1/bc.1
install -Dm644 manuals/dc.1 %{buildroot}%{_mandir}/man1/dc.1

%files
/usr/bin/bc
/usr/bin/dc
/usr/share/man/man1/bc.1.gz
/usr/share/man/man1/dc.1.gz
/usr/share/locale/


%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 7.0.3
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- added missing changelog :)
