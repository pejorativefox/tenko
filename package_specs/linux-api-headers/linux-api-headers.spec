Name:       linux-api-headers
Version:    7.2.4
Release:    1
Summary:    Linux userspace API headers
License:    GPL2
Prefix:     /usr

Provides: kernel-headers = %{version}-%{release}

%description
Linux UAPI headers required to compile C programs (linux/limits.h and
friends). This is a bootstrap package for the build container; phase 2
replaces it with headers generated from the pinned kernel source.

%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/include
for d in asm asm-generic cxl drm fwctl linux misc mtd rdma regulator scsi sound video xen; do
    cp -a /usr/include/$d %{buildroot}/usr/include/
done

%files -f %{_sourcedir}/linux-api-headers.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 7.2.4
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 7.2.4
- Bootstrap UAPI headers for the build container
