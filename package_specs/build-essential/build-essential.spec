Name:       build-essential
Version:    0.1
Release:    4
Summary:    Meta-package for build tools.
License:    MIT

Requires: gcc, patch, binutils, linux-headers, make, diffutils
Requires: tar, gzip, sed, gawk, flex, bison

%description
A meta-package for installing the most basic build tools.

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.1-4
- Drop gcc-devel: the headers and static libraries now ship in gcc
  (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.1-3
- Require gcc-devel after the gcc toolchain split

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 0.1
- Initial RPM

