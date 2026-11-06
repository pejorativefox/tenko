Name:       cpio
Version:    2.15
Release:    2
Summary:    GNU cpio copies files into or out of a cpio or tar archive
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
GNU cpio copies files into or out of a cpio or tar archive.  The archive
can be another file on the disk, a magnetic tape, or a pipe.

%package lang
Summary:    cpio translations
Requires:   cpio = %{version}-%{release}

%description lang
Translations for cpio.

%prep
%setup -q

# gcc15 workaround from the base set
sed -e "/^extern int (\*xstat)/s/()/(const char * restrict,  struct stat * restrict)/" \
    -i src/extern.h
sed -e "/^int (\*xstat)/s/()/(const char * restrict,  struct stat * restrict)/" \
    -i src/global.c

%build
%configure --enable-mt --with-rmt=/usr/libexec/rmt
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -rf %{buildroot}/usr/libexec/rmt
rm -f %{buildroot}/usr/share/info/dir
rm -rf %{buildroot}/usr/share/man

%files -f %{_sourcedir}/cpio.filelist
%files lang -f %{_sourcedir}/cpio-lang.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.15-2
- Split lang payload into cpio-lang (size audit)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.15
- Update to cpio 2.15
- Add the gcc15 xstat prototype workaround
- Required by dracut for initramfs creation
