Name:       libxdg-basedir
Version:    1.2.3
Release:    1
Summary:    Implementation of the XDG Base Directory specification
License:    GPL3
Prefix:     /usr
URL:        https://github.com/devnev/libxdg-basedir
Source0:    %{name}-%{version}.tar.gz

%description
libxdg-basedir is a small library implementing the XDG Base Directory
specification, used by awesome to locate configuration, data and cache
directories.

%prep
%setup -q -n %{name}-%{name}-%{version}

%build
./autogen.sh
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxdg-basedir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.3-1
- Update to 1.2.3; not in the r13.1 book, latest upstream
  stable 2026-11-05 (tag libxdg-basedir-1.2.3).
- Build from the upstream GitHub archive; the extracted top
  directory is libxdg-basedir-libxdg-basedir-1.2.3.
