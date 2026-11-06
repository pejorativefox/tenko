Name:       dnf
Version:    4.24.0
Release:    4
Summary:    Package manager for RPM based distributions
License:    GPL-2.0-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

Requires:   libdnf = 0.76.0
Requires:   libcomps >= 0.1.24
Requires:   libmodulemd >= 2.15.3
Requires:   python3-rpm
Requires:   /usr/bin/python3
Requires:   coreutils

%description
dnf is the package manager used to install the Tenko repository.  This
is the current release of the dnf 4 branch (Python based), which supports
the rpm 4.18.1 shipped in the base system.

%package lang
Summary:    dnf translations
Requires:   dnf = %{version}-%{release}

%description lang
Translations for dnf.

%prep
%setup -q

%build
mkdir build
pushd build
cmake -DPYTHON_DESIRED=3          \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -DWITH_MAN=0                \
      ..
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} cmake --install .
popd
# Python's sys.path uses /usr/lib64 for this distro.
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi
ln -sfv dnf-3 %{buildroot}%{_bindir}/dnf
ln -sfv dnf-automatic-3 %{buildroot}%{_bindir}/dnf-automatic

%files -f %{_sourcedir}/dnf.filelist
%files lang -f %{_sourcedir}/dnf-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.24.0-4
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): COPYING and dnf/__init__.py (issue #8).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.24.0-3
- Rebuild for Python 3.15 (3.14 site-packages are gone); 2 paths updated.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.24.0-2
- Split lang payload into dnf-lang (size audit)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.24.0-1
- Update to 4.24.0 (was 4.16.2) for the E1 self-hosted repo/rootfs
  assembly work.  dnf is not in the base set.  dnf 5 requires rpm >= 4.19, so
  the dnf 4 branch is used with the rpm 4.18.1 base.
- Installs dnf, dnf-automatic, the Python modules, config, systemd units
  and bash completion in one package (no yum-compat subpackages).
- Use a generated static filelist.
