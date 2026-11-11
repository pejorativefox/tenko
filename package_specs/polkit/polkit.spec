Name:       polkit
Version:    128
Release:    4
Summary:    Authorization toolkit for unprivileged processes
License:    LGPL-2.0-or-later
URL:        https://github.com/polkit-org/polkit
Prefix:     /usr
Source0:    polkit-128.tar.gz
Requires(pre): shadow
BuildRequires: duktape
BuildRequires: dbus-daemon
BuildRequires: gobject-introspection

%description
polkit is a toolkit for defining and handling authorizations. It allows
unprivileged processes to speak to privileged processes.

Requires: shadow >= 4.6

%post
groupadd -fg 27 polkitd &&
useradd -c "PolicyKit Daemon Owner" -d /etc/polkit-1 -u 27 \
        -g polkitd -s /bin/false polkitd

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release -D man=false -D session_tracking=logind -D authfw=shadow -D tests=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%package gir
Summary:    GObject Introspection data for polkit
License:    LGPL-2.0-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for polkit, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/polkit.filelist
%files gir -f %{_sourcedir}/polkit-gir.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 128-4
- Add Requires(pre): shadow; the %pre scriptlet runs groupadd/useradd, which failed in a minimal root.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 128-3
- Replace the TODO summary/description and record the verified license
  (LGPL-2.0-or-later): meson.build (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 128-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 128-1
- Update to 128 (current upstream, D9 parity)
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 127-3
- Split devel payload into polkit-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 127
- Sync with 0.115

* Sun May 10 2020 Chris Statzer <chris.statzer@qq.com> 0.115
- Updated post install to create proper polkitd user

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.115
- Initial RPM

