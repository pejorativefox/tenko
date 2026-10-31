Name:       libdrm
Version:    2.4.134
Release:    1
Summary:    Userspace interface to kernel DRM services
License:    MIT
Prefix:     /usr
Source0:    libdrm-2.4.134.tar.xz

%description
libdrm provides a userspace library for the kernel Direct Rendering Manager.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release -Dudev=true -Dtests=false -Dvalgrind=disabled
ninja
popd

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libdrm.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.4.134-1
- Initial package (BLFS r13.1)
