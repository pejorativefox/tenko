Name:       python-markupsafe
Version:    3.0.4
Release:    4
Summary:    Safely add untrusted strings to HTML/XML markup.
License:    BSD-3-Clause
Source0:    markupsafe-3.0.4.tar.gz
Prefix:     /usr
BuildRequires: python-setuptools
%description
Safely add untrusted strings to HTML/XML markup.

%prep
%setup -n markupsafe-%{version}

%build

%install
rm -rf %{buildroot}
MARKUPSAFE_PURE_PYTHON=1 python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python-markupsafe.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 3.0.4-4
- Rebuild with tenko-rpm-config 6-4: python(abi) = 3.15 is generated, so drop the explicit Requires: python.

* Wed Nov 11 2026 tenko <build@tenko.invalid> 3.0.4-3
- Require python: Tenko has no Python dependency generator, so the module package shipped without any runtime requirement.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.0.4-2
- Replace the legacy short licence name with the verified SPDX expression
  (BSD-3-Clause): LICENSE.txt (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.0.4-1
- Sync with the base set

* Mon Nov 02 2026 browneye <build@browneye.invalid> 3.0.3-2
- Rebuild for Python 3.15 (3.14 site-packages are gone); 3 paths updated.

* Fri Oct 30 2026 browneye <build@browneye.invalid> 3.0.3
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump

* Sun May 24 2020 Chris Statzer <chris.statzer@qq.com> 1.1.1-1
- Initial rpm package
