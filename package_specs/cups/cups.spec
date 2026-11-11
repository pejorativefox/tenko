Name:       cups
Version:    2.4.20
Release:    4
Summary:    Open source printing system
License:    Apache
URL:        https://openprinting.github.io/cups/
Source0:    %{name}-%{version}-source.tar.gz
Patch0:     %{name}-%{version}-upstream_fix-1.patch
Prefix:     /usr
Requires(pre): shadow

%description
CUPS is a standards-based, open source printing system developed by Apple Inc.

%pre
# On a fresh dnf --installroot transaction the systemd sysusers run that
# would create the lp group may happen after this scriptlet, and cups is
# pulled in directly by a library dependency (libcups.so.2) rather than
# through systemd.  Create both groups (gid 9 and 19 match the book) and
# the lp user idempotently so %pre does not depend on scriptlet order.
getent group lp >/dev/null || groupadd -g 9 lp
getent group lpadmin >/dev/null || groupadd -g 19 lpadmin
getent passwd lp >/dev/null || useradd -c "Print Service User" \
    -d /var/spool/cups -g lp -s /bin/false -u 9 lp

%prep
%setup -q
%patch -P 0 -p1

%build
%configure --libdir=/usr/lib            \
           --with-rundir=/run/cups      \
           --with-system-groups=lpadmin \
           --with-docdir=/usr/share/cups/doc-%{version}
%make_build

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install
mkdir -p %{buildroot}/usr/share/doc
ln -sfn ../cups/doc-%{version} %{buildroot}/usr/share/doc/cups-%{version}

%files -f %{_sourcedir}/cups.filelist

%changelog
* Mon Nov 09 2026 tenko <build@tenko.invalid> 2.4.20-4
- Create the lp group in %pre when it is absent.  A fresh
  dnf --installroot transaction pulled cups in through libcups.so.2
  (google-chrome-bin) without ordering systemd's sysusers run first, so
  useradd -g lp failed with "group 'lp' does not exist" and the whole
  package transaction aborted.  Both groups now use the book gids
  (lp 9, lpadmin 19) and every step stays idempotent.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.4.20-3
- Requires(pre) shadow: the %pre useradd/groupadd needs it.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.4.20-2
- %pre creates the lp user when absent (the lp group already exists);
  cupsd drops privileges to it at runtime.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.4.20-1
- Sync with the base set

* Fri Sep 04 2020 Chris Statzer <chris.statzer@qq.com> 2.3.3
- Initial RPM

