Name:       libisoburn
Version:    1.5.8.pl02
Release:    1
Summary:    Frontend for libburn and libisofs (xorriso, xorrisofs, osirrox)
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: libburn, libisofs, pkgconf
Requires:   libburn, libisofs

%description
libisoburn is a frontend for the libburn and libisofs libraries, enabling
creation and expansion of ISO-9660 filesystems on CD/DVD/BD media and on
plain files or block devices.  It provides the xorriso, xorrisofs, osirrox
and xorrecord commands used by the Tenko UEFI installer to produce hybrid
BIOS/UEFI bootable ISOs.

This package replaces the stale standalone xorriso 1.5.6 template: upstream
merged xorriso into libisoburn; it is packaged from here.

%prep
# Upstream ships 1.5.8.pl02 in a directory named after the 1.5.8 base.
%setup -q -n %{name}-1.5.8

%build
%configure --disable-static --enable-pkg-check-modules
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir* %{buildroot}%{_libdir}/libisoburn.la
# The Tk frontend needs /usr/bin/wish, and tk is not part of the Tenko
# base set.  It lists tk as optional; the installer only needs
# xorriso/xorrisofs/osirrox/xorrecord.
rm -vf %{buildroot}%{_bindir}/xorriso-tcltk \
      %{buildroot}%{_mandir}/man1/xorriso-tcltk.1 \
      %{buildroot}%{_infodir}/xorriso-tcltk.info

%files -f %{_sourcedir}/libisoburn.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.5.8.pl02-1
- Initial package
- Provides xorriso/xorrisofs/osirrox/xorrecord; supersedes the stale
  standalone xorriso 1.5.6 spec, which upstream folded into libisoburn
- Build with --disable-static --enable-pkg-check-modules as the base build specifies
