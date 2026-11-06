Name:       libsndfile
Version:    1.2.2
Release:    2
Summary:    Library for reading and writing sampled audio files
License:    LGPL-2.1-or-later AND Apache-2.0
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz


%description
libsndfile is a library of C routines for reading and writing files
containing sampled audio data. It supports a wide range of audio file
formats and is used by many audio applications and libraries.

%prep
%setup -a 0 

%build
sed -i '/typedef enum/,/bool ;/d' src/ALAC/alac_{en,de}coder.c
%configure --docdir=/usr/share/doc/libsndfile-%{version}  --disable-static \
            --docdir=/usr/share/doc/libsndfile-1.0.28
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/sndfile-cmp
/usr/bin/sndfile-concat
/usr/bin/sndfile-convert
/usr/bin/sndfile-deinterleave
/usr/bin/sndfile-info
/usr/bin/sndfile-interleave
/usr/bin/sndfile-metadata-get
/usr/bin/sndfile-metadata-set
/usr/bin/sndfile-play
/usr/bin/sndfile-salvage
/usr/include/sndfile.h
/usr/include/sndfile.hh
/usr/lib64/libsndfile.so
/usr/lib64/libsndfile.so.1
/usr/lib64/libsndfile.so.1.0.37
/usr/lib64/pkgconfig/sndfile.pc
/usr/share/doc/libsndfile-1.0.28/FAQ.md
/usr/share/doc/libsndfile-1.0.28/api.md
/usr/share/doc/libsndfile-1.0.28/bugs.md
/usr/share/doc/libsndfile-1.0.28/command.md
/usr/share/doc/libsndfile-1.0.28/embedded_files.md
/usr/share/doc/libsndfile-1.0.28/formats.md
/usr/share/doc/libsndfile-1.0.28/index.md
/usr/share/doc/libsndfile-1.0.28/libsndfile.css
/usr/share/doc/libsndfile-1.0.28/libsndfile.jpg
/usr/share/doc/libsndfile-1.0.28/lists.md
/usr/share/doc/libsndfile-1.0.28/new_file_type_howto.md
/usr/share/doc/libsndfile-1.0.28/octave.md
/usr/share/doc/libsndfile-1.0.28/print.css
/usr/share/doc/libsndfile-1.0.28/sndfile_info.md
/usr/share/doc/libsndfile-1.0.28/tutorial.md
/usr/share/doc/libsndfile-1.0.28/win32.md
/usr/share/man/man1/sndfile-cmp.1.gz
/usr/share/man/man1/sndfile-concat.1.gz
/usr/share/man/man1/sndfile-convert.1.gz
/usr/share/man/man1/sndfile-deinterleave.1.gz
/usr/share/man/man1/sndfile-info.1.gz
/usr/share/man/man1/sndfile-interleave.1.gz
/usr/share/man/man1/sndfile-metadata-get.1.gz
/usr/share/man/man1/sndfile-metadata-set.1.gz
/usr/share/man/man1/sndfile-play.1.gz
/usr/share/man/man1/sndfile-salvage.1.gz

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.2-2
- Replace the TODO summary/description and record the verified license
  (LGPL-2.1-or-later AND Apache-2.0): COPYING, src/ALAC/alac_encoder.c (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.2.2-1
- Sync with the base set

# let's skip this for now

