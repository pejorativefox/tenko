Name:       polkit
Version:    127
Release:    2
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    polkit-127.tar.gz

%description
TODO

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

%files -f %{_sourcedir}/polkit.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 127
- Sync with BLFS r13.1 (0.115)

* Sun May 10 2020 Chris Statzer <chris.statzer@qq.com> 0.115
- Updated post install to create proper polkitd user

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.115
- Initial RPM

