# Google Chrome is proprietary and is not in LFS/BLFS, so the version-parity
# rule in AGENTS.md cannot be satisfied from the books.  The user explicitly
# approved this binary-repackage exception (2026-11-03).
#
# Google no longer publishes a Linux tarball.  The official Google yum-repo
# RPM is the only binary distribution; its payload is already rooted at
# /opt/google/chrome (Prefix: /opt).  The source RPM named in its metadata is
# not published by Google, so this package repackages the signed binary RPM.
#
# The upstream Google yum/zypper repository setup, signing-key import, daily
# cron job, update-alternatives registration and AppArmor profile are
# intentionally not shipped.  Tenko owns updates and installs the hicolor
# icons directly instead of running xdg-icon-resource from %post.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

# Chrome is ~445 MiB installed; gzip makes a ~196 MiB RPM.  xz at level 6
# produces ~150 MiB without a large build-time cost.
%global _binary_payload w6.xzdio

Name:       google-chrome-bin
Version:    156.0.8078.79
Release:    1
Summary:    Google Chrome web browser (official upstream x86_64 RPM repackaged)
License:    Proprietary (Google Chrome Terms of Service)
URL:        https://chrome.google.com/
Prefix:     /opt
ExclusiveArch: x86_64

# Pinned full-version URL; the _current_ URL is mutable.
# size 148833873
# md5    aa265f25739ca1c81b5a64a06f51b56e
# sha256 0399d98f1ee16eccb39fb14a3461b25b2d5ae093f96a9b585cfb54f0a6a67c1a
# signed by Google Chrome key ID c264648f
Source0:    google-chrome-stable-%{version}-1.x86_64.rpm

# Prebuilt payload: do not let rpm guess dependencies from /opt.  The explicit
# list below is what the chrome binary actually needs on tenko.
AutoProv: no
AutoReq: no

Provides:   google-chrome = %{version}-%{release}
Provides:   google-chrome-stable = %{version}-%{release}
Provides:   web_browser

# ca-certificates is provided by make-ca in tenko.
Requires:   ca-certificates
Requires:   desktop-file-utils
Requires:   hicolor-icon-theme
Requires:   liberation-fonts
Requires:   xdg-utils
Requires:   ld-linux-x86-64.so.2()(64bit)
Requires:   libc.so.6()(64bit)
Requires:   libm.so.6()(64bit)
Requires:   libdl.so.2()(64bit)
Requires:   libpthread.so.0()(64bit)
Requires:   libgcc_s.so.1()(64bit)
Requires:   libX11.so.6()(64bit)
Requires:   libXcomposite.so.1()(64bit)
Requires:   libXdamage.so.1()(64bit)
Requires:   libXext.so.6()(64bit)
Requires:   libXfixes.so.3()(64bit)
Requires:   libXrandr.so.2()(64bit)
Requires:   libxcb.so.1()(64bit)
Requires:   libxkbcommon.so.0()(64bit)
Requires:   libasound.so.2()(64bit)
Requires:   libatk-1.0.so.0()(64bit)
Requires:   libatk-bridge-2.0.so.0()(64bit)
Requires:   libatspi.so.0()(64bit)
Requires:   libcairo.so.2()(64bit)
Requires:   libcups.so.2()(64bit)
Requires:   libdbus-1.so.3()(64bit)
Requires:   libexpat.so.1()(64bit)
Requires:   libfontconfig.so.1()(64bit)
Requires:   libgbm.so.1()(64bit)
Requires:   libgdk_pixbuf-2.0.so.0()(64bit)
Requires:   libgio-2.0.so.0()(64bit)
Requires:   libglib-2.0.so.0()(64bit)
Requires:   libgobject-2.0.so.0()(64bit)
Requires:   libgtk-3.so.0()(64bit)
Requires:   libnspr4.so()(64bit)
Requires:   libnss3.so()(64bit)
Requires:   libnssutil3.so()(64bit)
Requires:   libsmime3.so()(64bit)
Requires:   libpango-1.0.so.0()(64bit)
Requires:   libudev.so.1()(64bit)

# Chrome ships its own libvulkan.so.1 under /opt/google/chrome and starts
# without the system vulkan-loader, so the upstream auto-requirement is a
# false positive for this repackage; do not require vulkan-loader.

%description
Google Chrome is a proprietary web browser from Google.

This package repackages the official Google Chrome x86_64 RPM under
/opt/google/chrome, with /usr/bin launchers, desktop entries, hicolor icons,
man pages and AppStream metadata.  Google no longer publishes a Linux
tarball, so the upstream RPM payload is the only binary distribution.

The Google yum/zypper repository setup, signing-key import, cron job and
update-alternatives registration from the upstream RPM are intentionally
not shipped; tenko owns updates.  The hicolor icons are installed by
the package instead of at post-install time.

Chrome is not in LFS/BLFS.  The user explicitly approved this package as an
exception to the version-parity rule for personal use.

%prep
rm -rf %{_builddir}/chrome-rpm
mkdir -p %{_builddir}/chrome-rpm
cd %{_builddir}/chrome-rpm
bsdtar -xf %{SOURCE0}

%build

%install
rm -rf %{buildroot}
install -d %{buildroot}/opt/google
cp -a %{_builddir}/chrome-rpm/opt/google/chrome %{buildroot}/opt/google/chrome

# Upstream-only integration: Google's repo/cron/apparmor/defaults helpers.
rm -rf %{buildroot}/opt/google/chrome/apparmor.d
rm -f  %{buildroot}/opt/google/chrome/default-app-block

install -d %{buildroot}%{_bindir}
ln -s /opt/google/chrome/google-chrome %{buildroot}%{_bindir}/google-chrome
ln -s /opt/google/chrome/google-chrome %{buildroot}%{_bindir}/google-chrome-stable

install -d %{buildroot}%{_datadir}/applications
install -m644 %{_builddir}/chrome-rpm/usr/share/applications/google-chrome.desktop \
    %{buildroot}%{_datadir}/applications/google-chrome.desktop
install -m644 %{_builddir}/chrome-rpm/usr/share/applications/com.google.Chrome.desktop \
    %{buildroot}%{_datadir}/applications/com.google.Chrome.desktop

install -d %{buildroot}%{_datadir}/metainfo
install -m644 %{_builddir}/chrome-rpm/usr/share/appdata/google-chrome.appdata.xml \
    %{buildroot}%{_datadir}/metainfo/google-chrome.appdata.xml

install -d %{buildroot}%{_mandir}/man1
install -m644 %{_builddir}/chrome-rpm/usr/share/man/man1/google-chrome-stable.1.gz \
    %{buildroot}%{_mandir}/man1/google-chrome-stable.1.gz
ln -s google-chrome-stable.1.gz %{buildroot}%{_mandir}/man1/google-chrome.1.gz

for size in 16 24 32 48 64 128 256; do
    install -d %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps
    install -m644 %{buildroot}/opt/google/chrome/product_logo_${size}.png \
        %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/google-chrome.png
done

%post
update-desktop-database %{_datadir}/applications &>/dev/null || :

%postun
update-desktop-database %{_datadir}/applications &>/dev/null || :

%files -f %{_sourcedir}/google-chrome-bin.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 156.0.8078.79-1
- Initial repackage of the official Google Chrome stable x86_64 RPM under
  /opt/google/chrome; drop Google's repo/cron/alternatives integration.
  User-approved LFS/BLFS exception; personal use.
