Name:       linux-api-headers
Version:    7.2.6
Release:    1
Summary:    Linux userspace API headers
License:    GPL-2.0-only WITH Linux-syscall-note
Prefix:     /usr
Source0:    linux-%{version}.tar.xz

Provides:   kernel-headers = %{version}-%{release}

%description
Sanitized Linux UAPI headers generated from the pinned Browneye kernel
source with "make headers_install".  This replaces the old bootstrap
package that copied the host's kernel-headers tree.

%prep
%setup -q -n linux-%{version}

%build
make mrproper
make headers

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr
cp -a usr/include %{buildroot}/usr/
find %{buildroot}/usr/include -type f ! -name '*.h' -delete

%files -f %{_sourcedir}/linux-api-headers.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 7.1.8-1
- Generate UAPI headers from the pinned kernel source (C9)
