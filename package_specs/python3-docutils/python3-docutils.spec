Name:       python3-docutils
Version:    0.23
Release:    2
Summary:    Python text processing system (docutils, rst2man)
License:    public domain / BSD / GPL
Prefix:     /usr
Source0:    docutils-%{version}.tar.gz

%description
Docutils is an open-source text processing system for processing plaintext
documentation into useful formats such as HTML, LaTeX, man pages, Open
Document and XML.  It provides rst2man, which GLib uses to build its man
pages.

%prep
%setup -q -n docutils-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-docutils.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.23-2
- Rebuild for Python 3.15 (3.14 site-packages are gone); 3 paths updated.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.23-1
- Update to the BLFS r13.1 version (0.23, was 0.16) and rebuild with the
  current pip/setuptools so it installs into /usr/lib64/python3.15.
- Build-time dependency of glib 2.90.0 (rst2man generates the GLib man
  pages) for the E1 dnf/libdnf chain.
- Use a generated static filelist.
