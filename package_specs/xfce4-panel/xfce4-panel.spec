Name:       xfce4-panel
Version:    4.20.8
Release:    1
Summary:    Panel for the Xfce desktop environment
License:    GPL2
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: libxfce4util
BuildRequires: garcon
BuildRequires: exo
BuildRequires: libxfce4windowing


%description
Panel for the Xfce desktop environment

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/xfce4-panel.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.8
- Sync with BLFS r13.1 (4.19.1)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.1
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.0
- Initial RPM

