Name:       libxaw
Version:    1.0.16
Release:    1
Summary:    Xt widget set
License:    MIT
Prefix:     /usr
Source0:    libXaw-1.0.16.tar.xz

BuildRequires: libxmu, libxpm

%description
Xaw is a widget set based on the X Toolkit Intrinsics (Xt) Library.

%prep
%setup -q -n libXaw-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxaw.filelist
%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.0.16
- Sync with BLFS r13.1 (libxaw 1.0.16)
* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.0.15-1
- Version bump
