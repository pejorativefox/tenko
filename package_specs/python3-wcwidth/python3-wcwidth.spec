Name:       python3-wcwidth
Version:    0.9.4
Release:    1
Summary:    Measures the displayed width of unicode strings in a terminal
License:    MIT
URL:        https://github.com/jquast/wcwidth
Source0:    wcwidth-%{version}.tar.gz
Prefix:     /usr
BuildArch:  noarch

BuildRequires: python-setuptools

%description
wcwidth implements the POSIX wcwidth() and wcswidth() functions in Python,
returning the number of terminal cells a unicode string occupies.

%prep
%setup -q -n wcwidth-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-wcwidth.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 0.9.4-1
- New package, not in the base set: latest upstream stable release
  (0.9.4, checked 2026-11-15); needed by urwid.
