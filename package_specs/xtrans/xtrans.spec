Name:       xtrans
Version:    1.6.0
Release:    2
Summary:    X Window System Protocols Transport layer
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/lib/libxtrans
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
%description
X Window System Protocols Transport laye

%prep
%setup -q

%build
%configure ICE_LIBS=-lpthread
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xtrans.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.6.0-2
- Record the verified license (MIT): COPYING (issue #8).

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.6.0
- Sync with 1.5.0

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.5.0-1
- Version bump
