Name:       libassuan
Version:    3.0.2
Release:    1
Summary:    IPC library used by GnuPG and related programs
License:    LGPL
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2

%description
libassuan is the IPC library used by some GnuPG related software.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libassuan.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 3.0.2-1
- Update to the BLFS r13.1 version (3.0.2, was 2.5.1) for the E1
  dnf/libdnf dependency chain (required by gpgme 2.2.0).
- Use a generated static filelist.
