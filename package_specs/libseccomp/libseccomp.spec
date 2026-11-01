Name:       libseccomp
Version:    2.6.1
Release:    1
Summary:    Seccomp userspace library
License:    LGPL
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Userspace library for the Linux seccomp filter.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libseccomp.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.6.0
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.6.0
- Bootstrap dependency for man-db/systemd
