Name:       xdotool
Version:    4.20260303.1
Release:    1
Summary:    Command-line X11 automation tool
License:    BSD-3-Clause
URL:        https://github.com/jordansissel/xdotool
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: gcc, make, pkgconf, perl
BuildRequires: libx11, libxtst, libxinerama, libxkbcommon

%description
xdotool is a command-line tool to simulate keyboard and mouse input and to
search for, focus and manipulate X11 windows.  The package also ships the
libxdo shared library, its header and pkg-config file.

xdotool 4.20260303.1 is the latest stable upstream release.

%prep
%setup -q

%build
%make_build PREFIX=%{_prefix} \
    INSTALLBIN=%{_bindir} INSTALLLIB=%{_libdir} \
    INSTALLMAN=%{_mandir} INSTALLINCLUDE=%{_includedir}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} LDCONFIG=: \
    PREFIX=%{_prefix} \
    INSTALLBIN=%{_bindir} INSTALLLIB=%{_libdir} \
    INSTALLMAN=%{_mandir} INSTALLINCLUDE=%{_includedir}

%files -f %{_sourcedir}/xdotool.filelist

%changelog
* Mon Nov 09 2026 tenko <build@tenko.invalid> 4.20260303.1-1
- Initial package: xdotool 4.20260303.1 (latest stable upstream release).
- Ship the CLI, libxdo shared library, xdo.h and libxdo.pc in one package
  (no -devel split); verified license BSD-3-Clause (COPYRIGHT).
