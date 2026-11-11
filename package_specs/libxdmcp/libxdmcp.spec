Name:       libXdmcp
Version:    1.1.5
Release:    3
Summary:    X Display Manager Control Protocol library
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/lib/libxdmcp
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: util-macros
BuildRequires: xorgproto

%description
libXdmcp is the X Display Manager Control Protocol library. It is used by X
display managers and X servers to manage remote login sessions.

%prep
%setup -q -a0

%build 
%configure
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxdmcp.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.1.5-3
- Bump the release so the rebuilt licence metadata supersedes the
  previously published 1.1.5-2 RPM (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.1.5-2
- Replace the TODO summary/description and record the verified license
  (MIT): COPYING (issue #8).

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.1.5
- Sync with 1.1.2

# let's skip this for now
