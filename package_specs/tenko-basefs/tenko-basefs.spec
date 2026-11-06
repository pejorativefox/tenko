Name:       tenko-basefs
Version:    1.0
Release:    2
# Tenko rename compatibility (issue #22).
Obsoletes: browneye-basefs < 1.0-2
Provides: browneye-basefs = %{version}-%{release}
Summary:    Base filesystem layout for Tenko Linux
License:    MIT
Prefix:     /
Provides:   filesystem(unmerged-sbin-symlinks)
Provides:   cmake-filesystem
Provides:   cmake-filesystem(x86-64)
Provides:   filesystem(merged-sbin-symlinks)
Provides:   filesystem(unmerged-usr-symlinks)
Provides:   filesystem(merged-usr-symlinks)

%description
Owns the base directory layout and the merged-/usr symlinks.

%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/{etc,usr/{bin,lib,lib64,sbin,include,libexec,share,src,local/{bin,lib,sbin}},var/{cache,log,mail,opt,spool,tmp,lib},run,root,boot,home,mnt,opt,srv}
chmod 1777 %{buildroot}/tmp 2>/dev/null || true
mkdir -p %{buildroot}/tmp %{buildroot}/var/tmp
chmod 1777 %{buildroot}/tmp %{buildroot}/var/tmp
chmod 0750 %{buildroot}/root
ln -sf usr/bin  %{buildroot}/bin
ln -sf usr/lib  %{buildroot}/lib
ln -sf usr/lib64 %{buildroot}/lib64
ln -sf usr/sbin %{buildroot}/sbin

%files
/bin
/lib
/lib64
/sbin
/etc
/usr/bin
/usr/lib
/usr/lib64
/usr/sbin
/usr/include
/usr/libexec
/usr/share
/usr/src
/usr/local/bin
/usr/local/lib
/usr/local/sbin
/var/cache
/var/log
/var/mail
/var/opt
/var/spool
/var/tmp
/var/lib
/run
/tmp
/root
/boot
/home
/mnt
/opt
/srv

%changelog
* Fri Nov 06 2026 tenko <build@tenko.invalid> 1.0-2
- Rename browneye-basefs to tenko-basefs and add versioned
  Obsoletes/Provides aliases for the Tenko 13.1 compatibility window.
- Clean up old browneye paths, units, presets and configuration.

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.0
- Merged-/usr layout
