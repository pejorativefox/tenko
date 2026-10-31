Name:       libxt
Version:    1.3.1
Release:    1
Summary:    X Toolkit Intrinsics library
License:    GPL3
Prefix:     /usr
Source0:    libXt-%{version}.tar.xz

BuildRequires: libsm

%description
X Toolkit Intrinsics library

%prep
%setup -q -n libXt-%{version}


%build
%configure --with-appdefaultdir=/etc/X11/app-defaults
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxt.filelist

%changelog
* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.3.0-1
- Version bump
