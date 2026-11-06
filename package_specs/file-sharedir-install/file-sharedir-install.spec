Name:       file-sharedir-install
Version:    0.14
Release:    1
Summary:    Install shared files for Perl distributions
License:    GPL+ or Artistic
Source0:    File-ShareDir-Install-0.14.tar.gz
Prefix:     /usr

%description
File::ShareDir::Install is a Perl build-time module that installs
distribution shared files into the vendor shared directory.

%prep
%setup -q -n File-ShareDir-Install-%{version}

%build
perl Makefile.PL INSTALLDIRS=vendor NO_PACKLIST=1 NO_PERLLOCAL=1
%make_build

%install
rm -rf %{buildroot}
%make_install
find %{buildroot} -name perllocal.pod -delete

%files -f %{_sourcedir}/file-sharedir-install.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.14-1
- Initial package; build dependency of File::ShareDir 1.118
