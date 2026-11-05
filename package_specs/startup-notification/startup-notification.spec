Name:       startup-notification
Version:    0.12
Release:    3
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
TODO

%package static
Summary:    startup-notification static libraries
Requires:   startup-notification = %{version}-%{release}

%description static
Static libraries for startup-notification.

%prep
%setup -q

%build
%configure
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/startup-notification.filelist
%files static -f %{_sourcedir}/startup-notification-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.12-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.12-2
- Split devel, static payload into startup-notification-devel, startup-notification-static (size audit)

# let's skip this for now

