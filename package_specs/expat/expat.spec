Name:       expat
Version:    2.8.4
Release:    2
Summary:    stream-oriented XML parser
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
stream-oriented XML parser

%package devel
Summary:    expat development files
Requires:   expat = %{version}-%{release}

%description devel
Development files for expat.

%prep
%setup -q

%build
%configure --disable-static \
           --docdir=/usr/share/doc/expat-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/expat.filelist
%files devel -f %{_sourcedir}/expat-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.8.4-2
- Split devel payload into expat-devel (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.8.3
- Sync with LFS r13.1

# let's skip this for now
