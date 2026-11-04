Name:       privoxy
Version:    4.2.0
Release:    1
Summary:    Non-caching web proxy with advanced filtering capabilities
License:    GPL-2.0-or-later
URL:        https://www.privoxy.org/
Source0:    %{name}-%{version}-stable-src.tar.gz
Source1:    privoxy.service
Source2:    privoxy.sysusers
Prefix:     /usr

%description
Privoxy is a non-caching web proxy with advanced filtering capabilities for
enhancing privacy, modifying web page data and HTTP headers, controlling
access, and removing ads and other obnoxious Internet junk.  It has a flexible
configuration and can be used on stand-alone systems and multi-user networks.

Privoxy is not part of LFS or BLFS r13.1; the user approved upstream 4.2.0
stable as the version-parity exception.  This build uses the required pcre2
and zlib libraries with Privoxy's default feature set.

%prep
%setup -q -n %{name}-%{version}-stable

# The release tarball ships configure.in and acconfig.h, not the generated
# configure script.
autoheader
autoconf

%build
%configure --prefix=/usr \
    --sbindir=/usr/sbin \
    --sysconfdir=/etc/privoxy \
    --localstatedir=/var
%make_build

%install
rm -rf %{buildroot}
%make_install

# The upstream install target runs as root during the build and therefore
# leaves the configuration and log files owned by root:root.  Privoxy drops
# privileges to the privoxy user (uid/gid 73) at runtime, so give it access.
chown -R 73:73 %{buildroot}/etc/privoxy %{buildroot}/var/log/privoxy
chmod 0750 %{buildroot}/etc/privoxy %{buildroot}/var/log/privoxy
chmod 0640 %{buildroot}/var/log/privoxy/logfile
find %{buildroot}/etc/privoxy -type f -exec chmod 0640 {} +

# This build has no TLS support, but the 4.2.0 default config enables a
# TLS-only directive.  Comment it out so startup does not log a spurious
# "unrecognized directive" error.
sed -i 's/^elliptic-curve-keys 1$/# elliptic-curve-keys 1/' \
    %{buildroot}/etc/privoxy/config

# systemd unit and sysusers entry.
install -vdm755 %{buildroot}%{_unitdir}
install -vm644 %{SOURCE1} %{buildroot}%{_unitdir}/privoxy.service
install -vdm755 %{buildroot}/usr/lib/sysusers.d
install -vm644 %{SOURCE2} %{buildroot}/usr/lib/sysusers.d/privoxy.conf

%pre
# The configuration and log files are owned by privoxy.  Create the account
# before rpm extracts them; %post below also runs systemd-sysusers for image
# builds that install with scriptlets disabled and for later consistency.
if ! getent group privoxy >/dev/null 2>&1; then
    groupadd -r -g 73 privoxy || :
fi
if ! getent passwd privoxy >/dev/null 2>&1; then
    useradd -r -u 73 -g privoxy -d /etc/privoxy -s /sbin/nologin \
        -c "Privoxy web proxy" privoxy || :
fi

%post
if [ -x /usr/bin/systemd-sysusers ]; then
    /usr/bin/systemd-sysusers /usr/lib/sysusers.d/privoxy.conf || :
fi

%files -f %{_sourcedir}/privoxy.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.2.0-1
- New package: upstream Privoxy 4.2.0 stable.
  Privoxy is not in LFS or BLFS r13.1; the user approved the current upstream
  stable release as the version-parity exception.
- Source: https://downloads.sourceforge.net/ijbswa/privoxy-4.2.0-stable-src.tar.gz
  md5 0fbfb01fe8ac03927974f3ae2b35ca80
  sha256 6f91267f81f626c416994db89ab62f4d09246eebf4754b81186e13a18ee9028f
- Default feature set: required pcre2 and zlib, no optional TLS inspection,
  Brotli or Zstandard.  Requires pcre2 10.48 and zlib 1.3.2 from the repo.
- Build with autoheader/autoconf (the release tarball has no generated
  configure), then configure with prefix=/usr, sysconfdir=/etc/privoxy and
  localstatedir=/var.
- Ship a systemd unit, a sysusers.d entry for the privoxy user (uid/gid 73),
  and the upstream HTML documentation.  Configuration files and the log
  directory are owned by privoxy so the daemon can read/write them after
  dropping privileges.
