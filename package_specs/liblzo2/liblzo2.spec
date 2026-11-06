Name:       liblzo2
Version:    2.10
Release:    2
Summary:    LZO is a portable lossless data compression library written in ANSI C.
License:    GPL-2.0-or-later
Source0:    lzo-%{version}.tar.gz
Prefix:     /usr

Provides:   lzo = %{version}-%{release}

%description
LZO is a portable lossless data compression library written in ANSI C.

%prep
%setup -n lzo-%{version}

%build
%configure --enable-shared  \
           --disable-static \
           --docdir=/usr/share/doc/lzo-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/liblzo2.filelist

%changelog
* Fri Nov 06 2026 browneye <build@browneye.invalid> 2.10-2
- Provide the BLFS page name (lzo) alongside the library package name, so
  btrfs-progs and the installer can depend on either
  (BLFS r13.1 general/genlib/lzo.xml, lzo 2.10).
- License re-verified against COPYING and the source headers
  (GPL-2.0-or-later).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.10-1
- Rebuild against the r13.1 toolchain.
- Basis: BLFS r13.1 general/genlib/lzo.xml (lzo 2.10).
- Configure per the book: --enable-shared --disable-static
  --docdir=/usr/share/doc/lzo-2.10.
- Static filelist generated from the install tree.
