Name:       flac
Version:    1.5.0
Release:    2
Summary:    Free Lossless Audio Codec
License:    BSD-3-Clause AND GPL-2.0-or-later AND LGPL-2.1-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz


%description
FLAC is open source software that can reduce the amount of storage space
needed to store digital audio signals without needing to remove information
in doing so. It includes the libFLAC and libFLAC++ libraries, the flac and
metaflac command line tools, and documentation.

%prep
%setup -a 0 

%build
%configure  --disable-thorough-tests
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/flac
/usr/bin/metaflac
/usr/include/FLAC++/all.h
/usr/include/FLAC++/decoder.h
/usr/include/FLAC++/encoder.h
/usr/include/FLAC++/export.h
/usr/include/FLAC++/metadata.h
/usr/include/FLAC/all.h
/usr/include/FLAC/assert.h
/usr/include/FLAC/callback.h
/usr/include/FLAC/export.h
/usr/include/FLAC/format.h
/usr/include/FLAC/metadata.h
/usr/include/FLAC/ordinals.h
/usr/include/FLAC/stream_decoder.h
/usr/include/FLAC/stream_encoder.h
/usr/lib64/libFLAC++.so
/usr/lib64/libFLAC++.so.11
/usr/lib64/libFLAC++.so.11.0.0
/usr/lib64/libFLAC.so
/usr/lib64/libFLAC.so.14
/usr/lib64/libFLAC.so.14.0.0
/usr/lib64/pkgconfig/flac++.pc
/usr/lib64/pkgconfig/flac.pc
/usr/share/aclocal/libFLAC++.m4
/usr/share/aclocal/libFLAC.m4
/usr/share/doc/flac/images/logo.svg
/usr/share/doc/flac/images/logo130.gif
/usr/share/man/man1/flac.1.gz
/usr/share/man/man1/metaflac.1.gz

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.5.0-2
- Replace the TODO summary/description and record the verified license
  (BSD-3-Clause AND GPL-2.0-or-later AND LGPL-2.1-or-later): README.md (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.5.0-1
- Sync with BLFS r13.1

# let's skip this for now

