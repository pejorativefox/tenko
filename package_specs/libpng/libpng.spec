Name:       libpng
Version:    1.6.59
Release:    4
Summary:    PNG reference library
License:    libpng-2.0
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

BuildRequires: zlib, pkgconf

Provides: pkgconfig(libpng)

%description
libpng is the reference implementation of the PNG (Portable Network
Graphics) image format. It provides a complete library for reading,
writing and manipulating PNG images.

%prep
%setup -q

%build
LIBS=-lpthread ./configure --prefix=/usr --disable-static --libdir=%{_libdir}
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
rm -vf %{buildroot}/usr/lib64/libpng.la

%files -f %{_sourcedir}/libpng.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.6.59-4
- Replace the TODO summary/description and record the verified license
  (libpng-2.0): LICENSE (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.6.59-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Mon Nov  2 2026 browneye <build@browneye.invalid> 1.6.59-1
- Update to 1.6.59 (current LFS/BLFS r13.1 trunk version).

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.6.58
- Sync with BLFS r13.1 (1.6.36)

# let's skip this for now

