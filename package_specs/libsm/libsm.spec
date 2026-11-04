Name:       libsm
Version:    1.2.6
Release:    2
Summary:    X Session Management Library
License:    GPL3
Prefix:     /usr
Source0:    libSM-1.2.6.tar.xz

BuildRequires: libice

%description
X Session Management Library

%package doc
Summary:    libsm documentation
Requires:   libsm = %{version}-%{release}

%description doc
Documentation for libsm.

%package static
Summary:    libsm static libraries
Requires:   libsm = %{version}-%{release}

%description static
Static libraries for libsm.

%package devel
Summary:    libsm development files
Requires:   libsm = %{version}-%{release}

%description devel
Development files for libsm.

%prep
%setup -q -n libSM-%{version}

%build
%configure
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libsm.filelist
%files doc -f %{_sourcedir}/libsm-doc.filelist
%files static -f %{_sourcedir}/libsm-static.filelist
%files devel -f %{_sourcedir}/libsm-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.2.6-2
- Split doc, static, devel payload into libsm-doc, libsm-static, libsm-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.2.6
- Sync with BLFS r13.1 (1.2.4)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.4-1
- Version bump
