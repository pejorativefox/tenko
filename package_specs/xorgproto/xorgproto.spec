Name:       xorgproto
Version:    2025.1
Release:    1
Summary:    Xorg Protocols
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Xorg Protocols

%prep
%setup -q

%build 
%configure
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xorgproto.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 2025.1
- Sync with BLFS r13.1 (2023.2)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 2023.2
- Version bump
