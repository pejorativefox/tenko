Name:       tenko-basefs
Version:    1.0
Release:    4
Summary:    Base filesystem layout for Tenko Linux
License:    MIT
URL:        https://pjfox.xyz/git/daspork/tenko
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
mkdir -p %{buildroot}/{etc,usr/{bin,lib,lib64,sbin,include,libexec,share,src,local/{bin,etc,games,include,lib,man,sbin,share,src}},var/{cache,log,mail,opt,spool,tmp,lib,local},run,root,boot,home,mnt,opt,srv,media}
chmod 1777 %{buildroot}/tmp 2>/dev/null || true
mkdir -p %{buildroot}/tmp %{buildroot}/var/tmp
chmod 1777 %{buildroot}/tmp %{buildroot}/var/tmp
chmod 0750 %{buildroot}/root
chmod 0755 %{buildroot}/media %{buildroot}/var/local
chmod 0755 %{buildroot}/usr/local/{etc,games,include,man,share,src}
ln -sf usr/bin  %{buildroot}/bin
ln -sf usr/lib  %{buildroot}/lib
ln -sf usr/lib64 %{buildroot}/lib64
ln -sf usr/sbin %{buildroot}/sbin

%files -f %{_sourcedir}/tenko-basefs.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 1.0-4
- Complete the FHS 3.0 layout: add /media, /var/local and the
  /usr/local/{etc,games,include,man,share,src} directories with root:root
  and mode 0755.  /var/run and /var/lock remain systemd tmpfiles symlinks
  (var.conf and legacy.conf) and are verified on a booted install
  (issue #34).

* Sat Nov 07 2026 tenko <build@tenko.invalid> 1.0-3
- Drop the browneye-basefs Obsoletes/Provides alias; no Browneye installs
  remain.

* Fri Nov 06 2026 tenko <build@tenko.invalid> 1.0-2
- Rename browneye-basefs to tenko-basefs and add versioned
  Obsoletes/Provides aliases for the Tenko 13.1 compatibility window.
- Clean up old browneye paths, units, presets and configuration.

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.0
- Merged-/usr layout
