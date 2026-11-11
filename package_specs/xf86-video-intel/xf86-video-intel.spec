Name:       xf86-video-intel
Version:    20230223
Release:    1
Summary:    Xorg Intel video driver
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/driver/xf86-video-intel
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
The Intel video driver for Xorg.

%prep
%setup -q

%build
# The 20230223 snapshot ships no generated configure script, so run
# autogen.sh (autoreconf) first and keep it from configuring twice.
NOCONFIGURE=1 ./autogen.sh
%configure --enable-kms-only --enable-uxa
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xf86-video-intel.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 20230223-1
- Keep 20230223: it is the latest upstream snapshot (the last tagged x.org
  release, 2.99.917, is older), matching the archived package page.  The
  package is not in the base set
- Build through autogen.sh because the tarball has no configure script
- Drop the stray mkdir of an /etc buildroot entry that nothing installs
