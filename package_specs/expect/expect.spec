Name:       expect
Version:    5.45.4
Release:    1
Summary:    Automation tool
License:    Public Domain
Source0:    %{name}%{version}.tar.gz
Patch0:     expect-5.45.4-gcc15-1.patch
Prefix:     /usr
BuildRequires: tcl

%description
Expect is a tool for automating interactive applications.

%prep
%setup -n %{name}%{version}
%patch -P 0 -p1

%build
CFLAGS="$CFLAGS -Wno-error=format-security"
%configure  --with-tcl=/usr/lib64  \
            --enable-shared         \
            --with-tclinclude=/usr/include
%make_build

%install
rm -rf %{buildroot}
%make_install
ln -svf expect5.45.4/libexpect5.45.4.so %{buildroot}/usr/lib
rm -rf %{buildroot}/usr/lib

%files -f %{_sourcedir}/expect.filelist

%changelog
* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 5.45.4
- Initial RPM

