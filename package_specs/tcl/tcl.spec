Name:       tcl
Version:    8.6.18
Release:    1
Summary:    The tcl programming language
License:    Tcl/Tk
Source0:    %{name}%{version}-src.tar.gz
Prefix:     /usr

%description
The tcl programming language

%prep
%setup -q -n tcl8.6.18

%build
export SRCDIR=$(pwd)
pushd unix
%configure
%make_build libdir=%{_libdir}

sed -e "s|$SRCDIR/unix|/usr/lib64|" \
    -e "s|$SRCDIR|/usr/include|"  \
    -i tclConfig.sh

sed -e "s|$SRCDIR/unix/pkgs/tdbc1.1.13|/usr/lib64/tdbc1.1.13|" \
    -e "s|$SRCDIR/pkgs/tdbc1.1.13/generic|/usr/include|"    \
    -e "s|$SRCDIR/pkgs/tdbc1.1.13/library|/usr/lib/64tcl8.6|" \
    -e "s|$SRCDIR/pkgs/tdbc1.1.13|/usr/include|"            \
    -i pkgs/tdbc1.1.13/tdbcConfig.sh

sed -e "s|$SRCDIR/unix/pkgs/itcl4.3.7|/usr/lib64/itcl4.3.7|" \
    -e "s|$SRCDIR/pkgs/itcl4.3.7/generic|/usr/include|"    \
    -e "s|$SRCDIR/pkgs/itcl4.3.7|/usr/include|"            \
    -i pkgs/itcl4.3.7/itclConfig.sh

unset SRCDIR
popd

%install
rm -rf %{buildroot}
pushd unix
%make_install
DESTDIR=%{buildroot} make install-private-headers
mv %{buildroot}/usr/lib %{buildroot}/usr/lib64
mkdir -p %{buildroot}/usr/lib
ln -sf tclsh8.6 %{buildroot}/usr/bin/tclsh
ln -sfn /usr/lib64/lib/tcl8.6 %{buildroot}/usr/lib/tcl8.6
popd

%files -f %{_sourcedir}/tcl.filelist

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 8.6.18
- Sync with LFS r13.1

* Tue Jun 13 2023 Chris Statzer <chris.statzer@gmail.com> 3.30.1
- Initial RPM

