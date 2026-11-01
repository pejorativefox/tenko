Name:       startup-notification
Version:    0.12
Release:    2
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
TODO

%package devel
Summary:    startup-notification development files
Requires:   startup-notification = %{version}-%{release}

%description devel
Development files for startup-notification.

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
%files devel -f %{_sourcedir}/startup-notification-devel.filelist
%files static -f %{_sourcedir}/startup-notification-static.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.12-2
- Split devel, static payload into startup-notification-devel, startup-notification-static (size audit)

# let's skip this for now

