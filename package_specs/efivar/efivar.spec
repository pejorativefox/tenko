Name:       efivar
Version:    39
Release:    1
Summary:    Tools and libraries to manipulate EFI variables
License:    LGPL-2.1
Source0:    %{name}-%{version}.tar.gz
Patch0:     efivar-39-upstream_fixes-1.patch
Prefix:     /usr

%description
Tools and libraries to work with EFI variables

%prep
%setup -q
%patch 0 -p1

%build
%make_build ENABLE_DOCS=0 ERRORS=

%install
rm -rf %{buildroot}
%make_install ENABLE_DOCS=0 LIBDIR=/usr/lib64
install -Dm644 docs/efivar.1 %{buildroot}/usr/share/man/man1/efivar.1
install -d %{buildroot}/usr/share/man/man3
install -m644 docs/*.3 %{buildroot}/usr/share/man/man3/

%files -f %{_sourcedir}/efivar.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 39-1
- Update to 39 (current BLFS r13.1, was 38)
- Apply the BLFS efivar-39-upstream_fixes-1.patch (glibc-2.43+ build fix)
- ENABLE_DOCS=0 and install the pre-generated man pages, as in BLFS
- Install the libraries into /usr/lib64, matching this distro's layout
- Ship a generated static filelist
