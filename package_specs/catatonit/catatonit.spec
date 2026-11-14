Name:       catatonit
Version:    0.2.1
Release:    1
Summary:    Minimal init process for containers
License:    GPL-2.0-or-later
URL:        https://github.com/openSUSE/catatonit
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

# -all-static links against libc.a.
BuildRequires: glibc
%description
catatonit is a tiny static init for containers: it reaps zombie
processes and forwards signals to its child.  podman uses it for
"podman run --init" and for the rootless pause process.

%prep
%setup -q

%build
autoreconf -fi
%configure
%make_build

%install
rm -rf %{buildroot}
install -D -m 0755 catatonit %{buildroot}%{_libexecdir}/catatonit/catatonit
install -d %{buildroot}%{_libexecdir}/podman
ln -s ../catatonit/catatonit %{buildroot}%{_libexecdir}/podman/catatonit

%files -f %{_sourcedir}/catatonit.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 0.2.1-1
- New package, not in the base set: latest upstream stable release
  (0.2.1, checked 2026-11-14).  Static container init for podman,
  replacing the catatonit in the podman-bin bundle; installed in
  /usr/libexec/catatonit with a podman/catatonit symlink.
