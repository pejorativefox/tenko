Name:       libcanberra
Version:    0.30
Release:    1
Summary:    libcanberra is an implementation of the XDG Sound Theme and Name Specifications
License:    GPL
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
libcanberra is an implementation of the XDG Sound Theme and Name Specifications

%prep
%setup

%build
%configure --disable-oss
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/

%changelog
* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 0.30
- Initial RPM

