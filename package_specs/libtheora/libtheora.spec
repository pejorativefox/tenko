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
- Keep 1.1.1: this is the version named in the BLFS r13.1 book
  (packages.ent and the archived archive/libtheora.xml page; the
  r13.1 libdriv page is commented out) and it is still the latest
  stable release.
- Follow the archived book page: fix the libpng 1.6 build and use
  --disable-static; make install does not install the examples.
- First Browneye build of the existing spec.
