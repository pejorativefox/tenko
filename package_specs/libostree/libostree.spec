Name:       libostree
Version:    2026.6
Release:    1
Summary:    Operating system and container binary deployment and upgrades
License:    LGPL
Source0:    libostree-%{version}.tar.xz
Prefix:     /usr

%description
libostree is a tool and library for deploying and managing bootable,
immutable filesystem trees.  Flatpak uses it as its content-addressed object
store.

libostree (ostree) is not in the BLFS r13.1 book, but Flatpak cannot be built
without it.  This spec tracks the current upstream release.

%prep
%setup -q

%build
%configure                     \
    --disable-man              \
    --disable-man-html         \
    --with-curl                \
    --without-soup             \
    --without-soup3            \
    --with-crypto=openssl      \
    --without-composefs        \
    --without-avahi            \
    --without-selinux          \
    --without-smack            \
    --without-dracut           \
    --without-mkinitcpio
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libostree.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 2026.6-1
- Update from 2019.6 to 2026.6.  ostree is not in BLFS r13.1, but Flatpak
  1.18.4 requires a modern libostree (>= 2020.8).  Built with the libcurl
  fetcher and OpenSSL crypto so Flatpak can pull repositories over HTTPS
  and verify signatures.
