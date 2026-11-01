Name:       garcon
Version:    4.20.0
Release:    2
Summary:    Implementation of the freedesktop.org menu specification
License:    LGPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: libxfce4ui

%description
Implementation of the freedesktop.org menu specification

%package doc
Summary:    garcon documentation
Requires:   garcon = %{version}-%{release}

%description doc
Documentation for garcon.

%package devel
Summary:    garcon development files
Requires:   garcon = %{version}-%{release}

%description devel
Development files for garcon.

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/garcon.filelist
%files doc -f %{_sourcedir}/garcon-doc.filelist
%files devel -f %{_sourcedir}/garcon-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.0-2
- Split doc, devel payload into garcon-doc, garcon-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with BLFS r13.1 (4.19.0)

* Wed Aug 30 2023  Chris Statzer <chris.statzer@gmail.com> 4.19.0

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.6.4
- Initial RPM

