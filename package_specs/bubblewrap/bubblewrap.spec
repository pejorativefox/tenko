Name:       bubblewrap
Version:    0.13.1
Release:    2
Summary:    Unprivileged sandboxing tool 
License:    LGPL-2.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Unprivileged sandboxing tool 

%prep
%setup

%build
mkdir build
pushd build
meson setup --prefix=/usr --buildtype=release ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files
/usr/bin/bwrap
/usr/share/bash-completion/completions/bwrap
/usr/share/zsh/site-functions/_bwrap

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.13.1-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.0-or-later): LICENSE, COPYING and the bubblewrap.c/network.c headers (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.13.1-1
- Sync with the base set

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.4.0
- Initial RPM

