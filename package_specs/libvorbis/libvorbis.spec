Name:       libvorbis
Version:    1.3.7
Release:    4
Summary:    Ogg Vorbis audio codec library
License:    BSD-3-Clause
URL:        https://github.com/xiph/vorbis
Prefix:     /usr
Source0:    libvorbis-1.3.7.tar.xz
BuildRequires: libogg

%description
Vorbis is a general purpose perceptual audio codec intended to allow maximum
encoder flexibility over a wide range of bitrates. libvorbis provides the
reference encoder and decoder libraries for the Ogg Vorbis format.

%prep
%setup -q

%build
%configure  --disable-static
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libvorbis.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.3.7-4
- Replace the TODO summary/description and record the verified license
  (BSD-3-Clause): COPYING (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.3.7-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.3.7
- Sync with 1.3.6

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.3.6-1
- Version bump

