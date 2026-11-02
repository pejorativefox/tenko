Name:       xml-parser
Version:    2.59
Release:    1
Summary:    Perl module for parsing XML documents
License:    GPL+ or Artistic
Source0:    XML-Parser-2.59.tar.gz
Prefix:     /usr

BuildRequires: expat-devel, file-sharedir-install, class-inspector

%description
XML::Parser is a Perl interface to James Clark's Expat XML parser, built on
top of XML::Parser::Expat.

%prep
%setup -q -n XML-Parser-%{version}

%build
perl Makefile.PL INSTALLDIRS=vendor NO_PACKLIST=1 NO_PERLLOCAL=1
%make_build

%install
rm -rf %{buildroot}
%make_install
find %{buildroot} -name perllocal.pod -delete

%files -f %{_sourcedir}/xml-parser.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.59-1
- Update to the BLFS r13.1 version (2.59, was the 2.46 LFS template) and
  build against the distro perl 5.44 vendor path; needed by intltool and
  therefore by lightdm
- Use a generated static filelist instead of the stale 5.38.0 path list

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 5.38
- Version bump
