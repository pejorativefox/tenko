Name:       libgcrypt
Version:    1.12.4
Release:    1
Summary:    GnuPG crypto library
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2

BuildRequires: libgpg-error

%description
The libgcrypt package contains a general purpose crypto library based on the
code used in GnuPG.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libgcrypt.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.12.4-1
- Update to the pinned version (1.12.4, was 1.10.2) for lightdm
- Use a generated static filelist: the libtool version changed, so the
  shipped library is now libgcrypt.so.20.8.9 (SONAME libgcrypt.so.20)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.10.2-1
- Version bump
