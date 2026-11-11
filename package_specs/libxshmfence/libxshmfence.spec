Name:       libxshmfence
Version:    1.3.3
Release:    2
Summary:    X SyncFence library
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
This library offers a CPU-based synchronization primitive compatible with the X SyncFence

%prep
%setup -q

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxshmfence.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.3.3-2
- Record the verified license (MIT): COPYING (issue #8).

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.3-1
- Version bump
