Name:       newt
Version:    0.52.25
Release:    3
Summary:    Newt is a programming library for color text mode
License:    LGPL-2.0-only
URL:        https://pagure.io/newt
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz
BuildRequires: slang
BuildRequires: tcl

%description
Newt is a programming library for color text mode

%prep
%setup -a 0

%build
sed -e 's/^LIBNEWT =/#&/' \
    -e '/install -m 644 $(LIBNEWT)/ s/^/#/' \
    -e 's/$(LIBNEWT)/$(LIBNEWTSONAME)/g' \
    -i Makefile.in
%configure --with-gpm-support
%make_build


%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/newt.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 0.52.25-3
- Rebuild with tenko-rpm-config 6-4 for the generated python(abi) = 3.15 requirement on its Python modules.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.52.25-2
- Record the verified license (LGPL-2.0-only): README (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.52.25-1
- Sync with the base set

* Wed May 20 2020 Chris Statzer <chris.statzer@qq.com> 1.11.0-2
- packaged the python2 files in a sub package to prevent being pulled in deps

