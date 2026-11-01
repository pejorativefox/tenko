Name:       polkit
Version:    127
Release:    3
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

%package devel
Summary:    polkit development files
Requires:   polkit = %{version}-%{release}

%description devel
Development files for polkit.

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
%files devel -f %{_sourcedir}/polkit-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 127-3
- Split devel payload into polkit-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 127
- Sync with BLFS r13.1 (0.115)

* Sun May 10 2020 Chris Statzer <chris.statzer@qq.com> 0.115
- Updated post install to create proper polkitd user

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.115
- Initial RPM

