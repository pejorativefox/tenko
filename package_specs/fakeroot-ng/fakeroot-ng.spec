Name:       fakeroot-ng
Version:    0.18
Release:    1
Summary:    Tool to simulate a root user for package builds.
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.gz
Patch0:     fakeroot-ng-0.18-sched.patch
Prefix:     /usr

%description
fakeroot-ng simulates a root user for package builds by intercepting the
relevant system calls with ptrace.

%prep
%setup -q
%patch0 -p1

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/fakeroot-ng.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.18-1
- Rebuild 0.18: not in the r13.1 book; latest upstream stable
  2026-11-05 (https://sourceforge.net/projects/fakerootng/).
- Add an explicit <sched.h> include: glibc 2.44 no longer exposes the
  CLONE_* constants through the headers process.cpp already had, and
  GCC 16 rejects the implicit uses.
