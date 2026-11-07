Name:       parse-yapp
Version:    1.21
Release:    1
Summary:    Perl module for generating LALR(1) parsers
License:    GPL-1.0-or-later OR Artistic-1.0-Perl
URL:        https://metacpan.org/release/Parse-Yapp
Source0:    Parse-Yapp-1.21.tar.gz
Prefix:     /usr

%description
Parse::Yapp compiles yacc-like LALR grammars into Perl object-oriented
parser modules.  It is required at build time by Samba's pidl tooling.

%prep
%setup -q -n Parse-Yapp-%{version}

%build
perl Makefile.PL INSTALLDIRS=vendor NO_PACKLIST=1 NO_PERLLOCAL=1
%make_build

%install
rm -rf %{buildroot}
%make_install
find %{buildroot} -name perllocal.pod -delete

%files
%{_bindir}/yapp
/usr/lib64/perl5/5.44.0/vendor_perl/Parse
%{_mandir}/man1/yapp.1.gz
%{_mandir}/man3/Parse::Yapp.3.gz

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 1.21-1
- New build-only package: Parse::Yapp 1.21 (latest CPAN release), needed
  by Samba's pidl tooling.
