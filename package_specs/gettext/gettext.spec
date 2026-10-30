Name:       gettext
Version:    1.0
Release:    1
Summary:    GNU Internationalization utilities
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
GNU Internationalization utilities

%prep
%setup -q

%build
CFLAGS="$CFLAGS -Wformat"
%configure --with-included-libxml --without-selinux --disable-static \
           --docdir=/usr/share/doc/gettext-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
chmod -v 0755 %{buildroot}/usr/lib64/preloadable_libintl.so
rm -rf %{buildroot}/usr/share/doc/gettext-%{version}/examples

%files
/usr/bin/
/usr/include/
/usr/lib64/gettext/
/usr/lib64/libasprintf.so*
/usr/lib64/libgettextlib*
/usr/lib64/libgettextpo.so*
/usr/lib64/libgettextsrc*
/usr/lib64/libtextstyle.so*
/usr/lib64/preloadable_libintl.so
/usr/libexec/gettext/
/usr/share/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.0
- Sync with LFS r13.1

# let's skip this for now
