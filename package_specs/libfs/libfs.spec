Name:       libfs
Version:    1.0.10
Release:    2
Summary:    X Font Service client library
License:    MIT-open-group
URL:        https://gitlab.freedesktop.org/xorg/lib/libfs
Prefix:     /usr
Source0:    libFS-%{version}.tar.xz
BuildRequires: util-macros
BuildRequires: xorgproto
BuildRequires: xtrans

%description
X Font Service client library

%prep
%setup -q -n libFS-%{version}


%build
%configure
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libfs.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.10-2
- Record the verified license (MIT-open-group): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.0.10-1
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.0.9-1
- Version bump
