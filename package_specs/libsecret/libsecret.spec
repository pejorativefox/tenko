Name:       libsecret
Version:    0.21.8.2
Release:    3
Summary:    GObject secret service library
License:    LGPL-2.1-or-later
URL:        https://gitlab.gnome.org/GNOME/libsecret
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

BuildRequires: libxslt
BuildRequires: libgcrypt

%description
The libsecret package contains a GObject based library for accessing the Secret Service API.

%prep
%setup -q

%build
mkdir build-libsecret
pushd build-libsecret
meson setup --prefix=/usr       \
            --buildtype=release \
            -Dbashcompdir=/usr/share/bash-completion/completions \
            -D gtk_doc=false    \
            -D manpage=false    \
            -D vapi=false       \
            ..
ninja
popd

%install    
rm -rf %{buildroot}
pushd build-libsecret
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir

%files -f %{_sourcedir}/libsecret.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 0.21.8.2-3
- Install the upstream secret-tool bash completion.  Meson only installed
  it when bash-completion.pc was present; set bashcompdir explicitly so the
  file is always packaged.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.21.8.2-2
- Record the verified license (LGPL-2.1-or-later): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.21.8.2-1
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.21.0-1
- Version bump

