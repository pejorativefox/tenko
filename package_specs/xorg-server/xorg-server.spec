Name:       xorg-server
Version:    21.1.24
Release:    1
Summary:    Xorg X11 server
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

BuildRequires: libx11, pixman, libdrm, libxkbfile, xtrans
BuildRequires: libepoxy, libxcvt, libtirpc, font-util
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
      -Dglx=false          \
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
* Sun Nov 01 2026 browneye <build@browneye.invalid> 21.1.24-1
- Sync with BLFS r13.1 (meson build)
