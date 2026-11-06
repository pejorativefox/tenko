Name:       class-inspector
Version:    1.36
Release:    1
Summary:    Get information about a class and its structure (Perl)
License:    GPL+ or Artistic
Source0:    Class-Inspector-1.36.tar.gz
Prefix:     /usr

%description
Class::Inspector provides an inspection interface for Perl classes: the
methods, source file, loaded state and inheritance information.

%prep
%setup -q -n Class-Inspector-%{version}

%build
perl Makefile.PL INSTALLDIRS=vendor NO_PACKLIST=1 NO_PERLLOCAL=1
%make_build

%install
rm -rf %{buildroot}
%make_install
find %{buildroot} -name perllocal.pod -delete

%files -f %{_sourcedir}/class-inspector.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.36-1
- Initial package; runtime dependency of File::ShareDir
