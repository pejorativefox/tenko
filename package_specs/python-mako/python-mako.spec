Name:       python-mako
Version:    1.4.3
Release:    2
Summary:    Python templating language
License:    MIT
Prefix:     /usr
Source0:    mako-1.4.3.tar.gz

Requires:   python-markupsafe
Requires: python

%description
Mako is a template library written in Python.  Mesa's build requires the
mako module (>= 0.8) when it generates its dispatch tables.

%prep
%setup -q -n mako-1.4.3

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files
/usr/bin/mako-render
/usr/lib64/python3.15/site-packages/

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 1.4.3-2
- Require python, not only python-markupsafe.

* Sun Nov 08 2026 browneye <build@browneye.invalid> 1.4.3-1
- Initial package: Mako 1.4.3, the latest stable upstream release.  Mesa's
  meson build requires the mako module when it generates its dispatch tables
  (issue #51).
