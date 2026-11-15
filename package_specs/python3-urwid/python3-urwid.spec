Name:       python3-urwid
Version:    5.1.3
Release:    1
Summary:    Console user interface library for Python
License:    LGPL-2.1-only
URL:        https://urwid.org/
Source0:    urwid-%{version}.tar.gz
Prefix:     /usr
BuildArch:  noarch

BuildRequires: python-setuptools
BuildRequires: python3-setuptools-scm
Requires:   python3-wcwidth

%description
Urwid is a console user interface library for Python with widgets, layout,
mouse support and unicode handling.

%prep
%setup -q -n urwid-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-urwid.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 5.1.3-1
- New package, not in the base set: latest upstream stable release
  (5.1.3, checked 2026-11-15); needed by auto-cpufreq.
