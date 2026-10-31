Name:       xcb-proto
Version:    1.17.0
Release:    1
Summary:    XML-XCB protocol library
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The xcb-proto package provides the XML-XCB protocol descriptions that libxcb uses to generate the majority of its code and API. 

%prep
%setup -q

%build 
%configure
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
mv %{buildroot}/usr/lib/* %{buildroot}/usr/lib64/
rm -rf %{buildroot}/lib
# xcb-proto installs xcbgen under site-packages; Python only searches
# /usr/lib64/python3.14/site-packages in this layout.
if [ -d %{buildroot}/usr/lib64/site-packages ]; then
    mkdir -p %{buildroot}/usr/lib64/python3.14
    mv %{buildroot}/usr/lib64/site-packages %{buildroot}/usr/lib64/python3.14/
fi

%files -f %{_sourcedir}/xcb-proto.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.17.0
- Sync with BLFS r13.1 (1.15)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.15-1
- Version bump
