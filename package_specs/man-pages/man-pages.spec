Name:       man-pages
Version:    6.20
Release:    2
Summary:    The Linux man-pages
License:    0BSD AND BSD-2-Clause AND BSD-3-Clause AND BSD-4-Clause-UC AND CC-BY-SA-4.0 AND GPL-1.0-or-later AND GPL-2.0-only AND GPL-2.0-or-later AND GPL-3.0-or-later AND LGPL-3.0-only WITH LGPL-3.0-linking-exception AND Linux-man-pages-1-para AND Linux-man-pages-copyleft AND Linux-man-pages-copyleft-2-para AND Linux-man-pages-copyleft-var AND MIT
URL:        https://www.kernel.org/doc/man-pages/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The Linux man-pages project documents the Linux kernel and C library interfaces that are employed by user-space programs.

%prep
%setup -q

%build
rm -v man3/crypt*

%install
rm -rf %{buildroot}
make -R install DESTDIR=%{buildroot} prefix=/usr GIT=false

%files -f %{_sourcedir}/man-pages.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 6.20-2
- Replace the legacy short licence name with the verified SPDX expression
  (0BSD AND BSD-2-Clause AND BSD-3-Clause AND BSD-4-Clause-UC AND CC-BY-SA-4.0 AND GPL-1.0-or-later AND GPL-2.0-only AND GPL-2.0-or-later AND GPL-3.0-or-later AND LGPL-3.0-only WITH LGPL-3.0-linking-exception AND Linux-man-pages-1-para AND Linux-man-pages-copyleft AND Linux-man-pages-copyleft-2-para AND Linux-man-pages-copyleft-var AND MIT): the LICENSES/ directory and the per-page SPDX headers (issue #8).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 6.20-1
- Update to 6.20 (current upstream version).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 6.18
- Sync with the base set

* Tue Jun 13 2023 Chris Statzer <chris.statzer@gmail.com> 3.30.1
- Initial RPM

