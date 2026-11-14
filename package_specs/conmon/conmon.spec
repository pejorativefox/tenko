Name:       conmon
Version:    2.2.1
Release:    1
Summary:    OCI container runtime monitor
License:    Apache-2.0
URL:        https://github.com/containers/conmon
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: glib
BuildRequires: libseccomp
BuildRequires: systemd

%description
conmon monitors a single OCI container runtime process: it holds the
container's terminal and stdio, writes the container log (files or the
systemd journal) and records the exit status.  podman starts one conmon
per container.

%prep
%setup -q

%build
# The Makefile enables seccomp notify only when this probe succeeds; fail
# instead of silently building without it.
test "$(hack/seccomp-notify.sh)" = 0
pkg-config --exists libsystemd
%make_build bin/conmon \
    CFLAGS="%{optflags} -std=gnu99" \
    GIT_COMMIT=v%{version}

%install
rm -rf %{buildroot}
make install.podman DESTDIR=%{buildroot} PREFIX=%{_prefix} \
    LIBEXECDIR=%{_libexecdir}

%files -f %{_sourcedir}/conmon.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 2.2.1-1
- New package, not in the base set: latest upstream stable release
  (2.2.1, checked 2026-11-14).  Replaces the conmon in the podman-bin
  bundle; built with journald logging and seccomp notify support.
  The man page needs go-md2man and is not shipped.
