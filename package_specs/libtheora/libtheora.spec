Name:       libtheora
Version:    1.1.1
Release:    1
Summary:    Theora video codec library
License:    BSD-3-Clause
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: libogg

%description
libtheora is the reference implementation of the Theora video
compression format developed by the Xiph.Org Foundation.

%prep
%setup -q

%build
sed -i 's/png_\(sizeof\)/\1/g' examples/png2theora.c
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libtheora.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.1.1-1
- Keep 1.1.1: this is the pinned version and it is still the latest
  stable release.
- Follow the archived package page: fix the libpng 1.6 build and use
  --disable-static; make install does not install the examples.
- First Browneye build of the existing spec.
