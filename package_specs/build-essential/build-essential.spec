Name:       build-essential
Version:    0.1
Release:    3
Summary:    Meta-package for build tools.
License:    MIT

Requires: gcc, gcc-devel, patch, binutils, linux-headers, make, diffutils
Requires: tar, gzip, sed, gawk, flex, bison

%description
A meta-package for installing the most basic build tools.

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.1-3
- Require gcc-devel after the gcc toolchain split

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 0.1
- Initial RPM

