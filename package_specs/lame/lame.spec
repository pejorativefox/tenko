Name:       lame
Version:    3.100
Release:    2
Summary:    mp3 encoder
License:    LGPL-2.0-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz


%description
The LAME package contains an MP3 encoder and optionally, an MP3 frame analyzer. 

%prep
%setup -q

%build
%configure --enable-mp3rtp --disable-static
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
mkdir -p %{buildroot}%{_libdir}/pkgconfig
cat > %{buildroot}%{_libdir}/pkgconfig/libmp3lame.pc << "EOF"
prefix=/usr
exec_prefix=${prefix}
libdir=${exec_prefix}/lib64
includedir=${prefix}/include

Name: libmp3lame
Description: LAME MP3 encoding library
Version: %{version}
Libs: -L${libdir} -lmp3lame
Cflags: -I${includedir}
EOF

%files -f %{_sourcedir}/lame.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.100-2
- Record the verified license (LGPL-2.0-or-later): COPYING and frontend/main.c (issue #8).

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 3.100
- Version bump
