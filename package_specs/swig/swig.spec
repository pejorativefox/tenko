Name:       swig
Version:    4.5.1
Release:    1
Summary:    Simplified Wrapper and Interface Generator
License:    BSD
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
SWIG is a software development tool that connects programs written in C
and C++ with a variety of high-level programming languages.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/swig.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.5.1-1
- Update to the BLFS r13.1 version (4.5.1, was 4.0.1) for the E1
  dnf/libdnf dependency chain (libdnf Python bindings).
- Use a generated static filelist.
