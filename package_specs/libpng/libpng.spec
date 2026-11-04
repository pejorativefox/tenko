Name:       libpng
Version:    1.6.59
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

BuildRequires: zlib, pkgconf

Provides: pkgconfig(libpng)

%description
TODO

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
* Mon Nov  2 2026 browneye <build@browneye.invalid> 1.6.59-1
- Update to 1.6.59 (current LFS/BLFS r13.1 trunk version).

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.6.58
- Sync with BLFS r13.1 (1.6.36)

# let's skip this for now

