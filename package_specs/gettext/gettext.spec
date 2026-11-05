Name:       gettext
Version:    1.0
Release:    3
Summary:    GNU Internationalization utilities
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

Requires:   gettext-libs = %{version}-%{release}
Requires:   gettext-tools = %{version}-%{release}

%description
GNU Internationalization utilities.  This package is a meta-package that
pulls in the runtime libraries and the build tools.

%package libs
Summary:    GNU gettext runtime libraries
License:    LGPL-2.1-or-later

%description libs
The GNU gettext runtime libraries: libintl (preloadable_libintl), libasprintf,
libgettextpo, libtextstyle and the private libgettextlib/libgettextsrc helper
libraries.  Packages that only need translated messages at runtime need this
package, not the gettext build tools.

%package tools
Summary:    GNU gettext build tools
License:    GPL-3.0-or-later
Requires:   gettext-libs = %{version}-%{release}

%description tools
The GNU gettext development and build tools, including xgettext, msgfmt,
msgmerge, msgcat and the rest of the msg* utilities, plus the headers,
autopoint/gettextize data and libtool/autoconf macros.

%package lang
Summary:    Translations for GNU gettext
License:    GPL-3.0-or-later
Requires:   gettext-libs = %{version}-%{release}

%description lang
Translated messages for the gettext tools and runtime.

%package doc
Summary:    Documentation for GNU gettext
License:    GFDL-1.2-or-later OR GPL-2.0-or-later

%description doc
Info, man and HTML documentation for GNU gettext.

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
%files libs -f %{_sourcedir}/gettext-libs.filelist
%files tools -f %{_sourcedir}/gettext-tools.filelist
%files lang -f %{_sourcedir}/gettext-lang.filelist
%files doc -f %{_sourcedir}/gettext-doc.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0-3
- Record the verified license (GPL-3.0-or-later): gettext-runtime/COPYING, gettext-runtime/intl/gettext.c and gettext-tools/doc/gettext.texi (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.0-2
- Split runtime libraries, build tools, translations and documentation;
  gettext is now a meta-package requiring gettext-libs and gettext-tools
  (size audit §7)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.0-1
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.0
- Sync with LFS r13.1

# let's skip this for now
