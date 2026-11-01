Name:       libwnck
Version:    43.3
Release:    1
Summary:    Library to manage X windows and workspaces (via pagers, tasklists, etc.)
License:    LGPL
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

Requires: startup-notification

%description
Library to manage X windows and workspaces (via pagers, tasklists, etc.)

%prep
%setup

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libwnck.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 43.1
- Sync with BLFS r13.1 (3.32.0)

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 3.32.0
- Initial RPM

