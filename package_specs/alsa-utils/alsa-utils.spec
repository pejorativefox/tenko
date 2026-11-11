Name:       alsa-utils
Version:    1.2.16
Release:    2
Summary:    Alsa Utilities
License:    GPL-2.0-or-later AND LGPL-2.1-or-later AND BSD-3-Clause
URL:        https://github.com/alsa-project/alsa-utils
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr
BuildRequires: alsa-lib
BuildRequires: python3-docutils

%description
The ALSA Utilities package contains various utilities which are useful for controlling your sound card. 

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/alsa-utils.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.16-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later AND LGPL-2.1-or-later AND BSD-3-Clause): COPYING, alsaucm/usecase.c and topology/nhlt/nhlt.h (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.2.16-1
- Sync with the base set

* Thu May 28 2020 Chris Statzer <chris.statzer@qq.com> 1.2.2
- Initial RPM

