Name:       libwnck
Version:    43.3
Release:    2
Summary:    Library to manage X windows and workspaces (via pagers, tasklists, etc.)
License:    LGPL
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

Requires: startup-notification

%description
Library to manage X windows and workspaces (via pagers, tasklists, etc.)

%package lang
Summary:    libwnck translations
Requires:   libwnck = %{version}-%{release}

%description lang
Translations for libwnck.

%package devel
Summary:    libwnck development files
Requires:   libwnck = %{version}-%{release}

%description devel
Development files for libwnck.

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
%files lang -f %{_sourcedir}/libwnck-lang.filelist
%files devel -f %{_sourcedir}/libwnck-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 43.3-2
- Split lang, devel payload into libwnck-lang, libwnck-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 43.1
- Sync with BLFS r13.1 (3.32.0)

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 3.32.0
- Initial RPM

