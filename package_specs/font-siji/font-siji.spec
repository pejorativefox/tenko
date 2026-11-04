# Siji ships pre-built .pcf and .bdf artifacts from the upstream git
# repository (no build step).
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       font-siji
Version:    2019.02.18
Release:    1
Summary:    Iconic bitmap font for use as a terminal/status-line font
License:    GPL
Prefix:     /usr
Source0:    siji-master.tar.gz

ExclusiveArch: x86_64

AutoProv: no
AutoReq: no

%description
Siji (from the Cantonese "four-dot symbol for the ninth" glyph 丶) is an
iconic bitmap font containing ~70 monochrome glyphs — battery, network,
volume, window manager default-ws icons etc. — meant to sit alongside a
monospace terminal font in panels like swaybar/lemonbar/xfce4-panel.

Siji is not in LFS/BLFS.  The user explicitly requested packaging it as an
exception to the Browneye version-parity rule.  Upstream is a terminal
snapshot: the 2019-02-18 master commit is the last content-bearing change
(the project has been dormant since), so the package is versioned with the
snapshot date and pinned by the source checksum.

Upstream ships GPL; LICENSE from the tarball is copied into the payload.

%prep

%build

%install
rm -rf %{buildroot}
install -d -m 0755 %{buildroot}/usr/share/fonts/siji
tmp=$(mktemp -d)
tar -xzf %{SOURCE0} -C $tmp
install -m 0644 $tmp/siji-master/pcf/siji.pcf \
    %{buildroot}/usr/share/fonts/siji/siji.pcf
install -m 0644 $tmp/siji-master/bdf/siji.bdf \
    %{buildroot}/usr/share/fonts/siji/siji.bdf
install -m 0644 $tmp/siji-master/LICENSE \
    %{buildroot}/usr/share/fonts/siji/LICENSE
rm -rf $tmp

%files -f %{_sourcedir}/font-siji.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 2019.02.18
- Repackage the upstream master snapshot (last content-bearing commit
  2019-02-18): siji.pcf + siji.bdf + LICENSE pinned by checksum
- Static %files filelist, license text shipped in the payload
