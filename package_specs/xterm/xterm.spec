Name:       xterm
Version:    412
Release:    1
Summary:    X11 terminal emulator
License:    MIT
URL:        https://invisible-island.net/xterm/
Prefix:     /usr
Source0:    xterm-412.tgz
BuildRequires: fontconfig
BuildRequires: freetype
BuildRequires: libice
BuildRequires: libx11
BuildRequires: libxaw
BuildRequires: libxext
BuildRequires: libxft
BuildRequires: libxinerama
BuildRequires: libxmu
BuildRequires: libxpm
BuildRequires: libxt



%description
X11 terminal emulator.

xterm is maintained at its pinned version and is built
with the standard autotools build inline in its spec.


%prep
%setup -q

%build
sed -i '/v0/{n;s/new:/new:kb=^?:/}' termcap &&
printf '\tkbs=\\177,\n' >> terminfo &&
export TERMINFO=/usr/share/terminfo
%configure --with-xinitdir=/etc/X11/app-defaults
%make_build
unset TERMINFO

%install    
rm -rf %{buildroot}
%make_install
make install-ti DESTDIR=%{buildroot}
rm -vf %{buildroot}%{_infodir}/dir*
rm -vrf %{buildroot}/usr/share/terminfo

%files -f %{_sourcedir}/xterm.filelist
%changelog
# let's skip this for now

