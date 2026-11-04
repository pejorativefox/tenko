Name:       file-sharedir
Version:    1.118
Release:    1
Summary:    Locate per-dist and per-module shared files (Perl)
License:    GPL+ or Artistic
Source0:    File-ShareDir-1.118.tar.gz
Prefix:     /usr

%description
File::ShareDir is a Perl module that locates per-distribution and
per-module shared files installed alongside the module.

%prep
%setup -q -n File-ShareDir-%{version}

%build
perl Makefile.PL INSTALLDIRS=vendor NO_PACKLIST=1 NO_PERLLOCAL=1
%make_build

%install
rm -rf %{buildroot}
%make_install
find %{buildroot} -name perllocal.pod -delete

%files -f %{_sourcedir}/file-sharedir.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.118-1
- Initial package (BLFS r13.1); needed by XML::Parser 2.59
