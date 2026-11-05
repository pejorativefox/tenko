Name:       mkfontdir
Version:    1.0.7
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2



%description
TODO

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/mkfontdir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.7-1
- Rebuild mkfontdir 1.0.7, the latest/final x.org release, with a
  real %changelog and a generated %files list. Not in the r13.1
  book (x.org archive-era tool); latest upstream stable 2026-11-05.
- WARNING: /usr/bin/mkfontdir is byte-identical to the copy shipped
  by mkfontscale 1.2.4 (BLFS r13.1), and mkfontscale also owns
  /usr/share/man/man1/mkfontdir.1.gz.  This package therefore
  conflicts with the published mkfontscale and must not be published
  as-is; mkfontscale already provides the mkfontdir command.
