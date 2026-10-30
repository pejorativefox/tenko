Name:       browneye-basefs
Version:    1.0
Release:    1
Summary:    Base filesystem layout for Browneye Linux
License:    MIT
Prefix:     /

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
* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.0
- LFS r13.1 merged-/usr layout
