Name:       libwnck
Version:    43.3
Release:    5
Summary:    Library to manage X windows and workspaces (via pagers, tasklists, etc.)
License:    LGPL-2.0-or-later
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

%package gir
Summary:    GObject Introspection data for libwnck
License:    LGPL-2.0-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for libwnck, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/libwnck.filelist
%files lang -f %{_sourcedir}/libwnck-lang.filelist
%files gir -f %{_sourcedir}/libwnck-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 43.3-5
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.0-or-later): COPYING, GNU Library GPL v2, plus libwnck/*.c "or any later version" (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 43.3-4
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 43.3-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 43.3-2
- Split lang, devel payload into libwnck-lang, libwnck-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 43.1
- Sync with 3.32.0

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 3.32.0
- Initial RPM

