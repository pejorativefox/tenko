Name:       man-pages
Version:    6.19
Release:    1
Summary:    The Linux man-pages
License:    Various
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The Linux man-pages project documents the Linux kernel and C library interfaces that are employed by user-space programs.

%prep
%setup -q

%build
rm -v man3/crypt*

%install
rm -rf %{buildroot}
make -R install DESTDIR=%{buildroot} prefix=/usr GIT=false

%files
/usr/bin/diffman-git
/usr/bin/grepc
/usr/bin/grepc_c
/usr/bin/grepc_mk
/usr/bin/mansect
/usr/bin/mansectf
/usr/bin/pdfman
/usr/bin/sortman
/usr/share/man

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 6.18
- Sync with LFS r13.1

* Tue Jun 13 2023 Chris Statzer <chris.statzer@gmail.com> 3.30.1
- Initial RPM

