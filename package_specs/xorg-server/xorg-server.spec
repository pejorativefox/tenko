Name:       xorg-server
Version:    21.1.25
Release:    2
Summary:    Xorg X11 server
License:    MIT
URL:        https://www.x.org/
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

BuildRequires: libx11, pixman, libdrm, libxkbfile, xtrans
BuildRequires: libepoxy, libxcvt, libtirpc, font-util
BuildRequires: libXdmcp
BuildRequires: libbsd
BuildRequires: libmd
BuildRequires: libpciaccess
BuildRequires: libxau
BuildRequires: libxext
BuildRequires: libxfont2
BuildRequires: libxshmfence
BuildRequires: mesa
BuildRequires: xorgproto
BuildRequires: dbus-daemon
BuildRequires: libxfixes
BuildRequires: libxslt
BuildRequires: xkbcomp
BuildRequires: freetype
BuildRequires: harfbuzz
BuildRequires: libfontenc
BuildRequires: libpng
BuildRequires: libxcb
BuildRequires: libxxf86vm
Requires:   xkbcomp
Requires:   xkeyboard-config
Requires:   xf86-input-libinput

%description
The Xorg X11 server, built X11-only with glamor and the setuid wrapper
(no systemd-logind session tracking).

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --localstatedir=/var --buildtype=release \
      -Dglamor=true        \
      -Dglx=true           \
      -Ddri3=true          \
      -Dsystemd_logind=false \
      -Dsuid_wrapper=true  \
      -Dxkb_output_dir=/var/lib/xkb
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*
mkdir -pv %{buildroot}/etc/X11/xorg.conf.d %{buildroot}/etc/sysconfig
cat > %{buildroot}/etc/sysconfig/createfiles << 'EOF'
/tmp/.ICE-unix dir 1777 root root
/tmp/.X11-unix dir 1777 root root
EOF
rm -f %{buildroot}/var/lib/xkb/README.compiled

%files -f %{_sourcedir}/xorg-server.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 21.1.25-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 21.1.25-1
- Update to 21.1.25.
- Drop the -Wl,-rpath-link,/usr/lib workaround: llvm-libs 23.1.0-3 installs
  into /usr/lib64, so libgallium's libLLVM dependency resolves normally.
* Sun Nov 01 2026 browneye <build@browneye.invalid> 21.1.24-2
- Split devel payload into xorg-server-devel (size audit)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 21.1.24-1
- Sync with the meson build
