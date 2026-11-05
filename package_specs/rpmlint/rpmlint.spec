Name:       rpmlint
Version:    2.10.0
Release:    1
Summary:    Tool for checking common errors in rpm packages
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
BuildRequires: python
BuildRequires: python-setuptools
BuildRequires: python-wheel

%description
rpmlint checks RPM packages and spec files for common packaging errors.

%prep
%setup -q -n %{name}-%{version}

%build
python3 -m pip wheel --no-build-isolation --no-deps -w dist .

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location \
    dist/*.whl
# The distro Python keeps its site-packages in /usr/lib64.
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/rpmlint.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.10.0-1
- Update 1.11 -> 2.10.0: not in the r13.1 book; latest upstream stable
  2026-11-05
  (https://github.com/rpm-software-management/rpmlint/releases).
- rpmlint is now a PEP 517 Python package: build a wheel with the
  declared setuptools backend (--no-build-isolation --no-deps) and
  install it with pip into the buildroot.  The 1.11 Makefile/tarball
  layout no longer exists.
- Runtime imports need tomli-w, pyxdg, pybeam, zstandard, pyenchant
  and python-magic, none of which are in the books or the Browneye
  repository; the package therefore builds and installs but cannot be
  executed yet.  See the build report for the exact import error.
