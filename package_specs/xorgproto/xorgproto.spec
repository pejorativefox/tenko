Name:       xorgproto
Version:    2026.1
Release:    2
Summary:    Xorg Protocols
License:    MIT
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Xorg Protocols

%package doc
Summary:    xorgproto documentation
Requires:   xorgproto = %{version}-%{release}

%description doc
Documentation for xorgproto.

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
%files doc -f %{_sourcedir}/xorgproto-doc.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2026.1-2
- Record the verified license (MIT): COPYING-x11proto (issue #8).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 2026.1-1
- Update to 2026.1 (current upstream version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2025.1-2
- Split doc payload into xorgproto-doc (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2025.1
- Sync with 2023.2

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 2023.2
- Version bump
