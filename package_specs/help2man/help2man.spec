Name:       help2man
Version:    1.49.3
Release:    1
Summary:    help2man produces simple manual pages from the ‘--help’ and ‘--version’ output of other commands.
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
help2man produces simple manual pages from the ‘--help’ and ‘--version’
output of other commands.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -f %{buildroot}%{_infodir}/dir

%files -f %{_sourcedir}/help2man.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.49.3-1
- Update 1.47.15 -> 1.49.3: not in the base set; latest upstream
  stable 2026-11-05 (https://ftp.gnu.org/gnu/help2man/).
- Build and install with the shipped autoconf/automake Makefile; the
  package is the Perl script plus its generated man page and info file.
  The translated man pages and message catalogs stay out because the
  base image has no Perl Locale::gettext, which makes upstream
  configure disable NLS (extra_make_install='') rather than fail.
