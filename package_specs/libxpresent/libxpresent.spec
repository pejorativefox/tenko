Name:       libxpresent
Version:    1.0.2
Release:    1
Summary:    Xlib Present extension library
License:    MIT
URL:        https://www.x.org/
Source0:    libXpresent-%{version}.tar.xz
Prefix:     /usr

BuildRequires: pkgconf
BuildRequires: xorgproto
BuildRequires: libx11
BuildRequires: libxext

%description
libXpresent provides the client library for the X Present extension, which
lets applications present rendered images to the screen with accurate frame
timing.  mpv's X11 video output uses it to pace presentation.

%prep
%setup -q -n libXpresent-%{version}

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/include/X11/extensions/Xpresent.h
/usr/lib64/libXpresent.so
/usr/lib64/libXpresent.so.1
/usr/lib64/libXpresent.so.1.0.0
/usr/lib64/pkgconfig/xpresent.pc
/usr/share/man/man3/XPresentFreeInput.3.gz
/usr/share/man/man3/XPresentNotifyMSC.3.gz
/usr/share/man/man3/XPresentPixmap.3.gz
/usr/share/man/man3/XPresentQueryCapabilities.3.gz
/usr/share/man/man3/XPresentQueryExtension.3.gz
/usr/share/man/man3/XPresentQueryVersion.3.gz
/usr/share/man/man3/XPresentSelectInput.3.gz
/usr/share/man/man3/XPresentVersion.3.gz
/usr/share/man/man3/Xpresent.3.gz

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 1.0.2-1
- New package: libXpresent 1.0.2, latest stable upstream.  Required by
  mpv 0.42's X11 video output.
