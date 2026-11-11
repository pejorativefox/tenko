Name:       libsndfile
Version:    1.2.2
Release:    2
Summary:    Library for reading and writing sampled audio files
License:    LGPL-2.1-or-later AND Apache-2.0
URL:        https://libsndfile.github.io/libsndfile/
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
BuildRequires: alsa-lib


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

%files -f %{_sourcedir}/libsndfile.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.2-2
- Replace the TODO summary/description and record the verified license
  (LGPL-2.1-or-later AND Apache-2.0): COPYING, src/ALAC/alac_encoder.c (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.2.2-1
- Sync with the base set

# let's skip this for now

