Name:       libxfont2
Version:    2.0.9
Release:    1
Summary:    X font handling library for server & utilities.
License:    GPL3
Prefix:     /usr
Source0:    libXfont2-%{version}.tar.xz

BuildRequires: libfontenc

%description
X font handling library for server & utilities.

%prep
%setup -q -n libXfont2-%{version}

%build
%configure --disable-devel-docs
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxfont2.filelist

%changelog
* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 2.0.6-1
- Version bump
