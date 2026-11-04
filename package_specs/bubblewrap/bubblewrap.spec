Name:       bubblewrap
Version:    0.13.1
Release:    1
Summary:    Unprivileged sandboxing tool 
License:    GPL
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
* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.13.1-1
- Sync with BLFS r13.1

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.4.0
- Initial RPM

