# Noto Sans Mono CJK SC is the Simplified Chinese monospace member of the
# Noto CJK family.  The release zip carries the complete weight range; Tenko
# installs Regular and Bold, which is what a terminal and the kmscon console
# need.  The fontconfig snippet makes the face a weak last-resort family for
# the generic families, so a Latin terminal font such as Terminus renders CJK
# instead of tofu.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       font-noto-cjk
Version:    2.004
Release:    1
Summary:    Noto Sans Mono CJK SC: Simplified Chinese monospace font
License:    OFL-1.1
URL:        https://github.com/notofonts/noto-cjk
Prefix:     /usr
Source0:    13_NotoSansMonoCJKsc.zip

ExclusiveArch: x86_64

AutoProv: no
AutoReq: no

%description
Noto Sans Mono CJK SC is a monospaced Simplified Chinese face from the Noto
CJK project.  It covers the GB 2312 / GB 18030 simplified Chinese repertoire
plus Latin, Greek, Cyrillic, punctuation and box drawing.

The package ships the Regular and Bold faces and a fontconfig snippet that
adds "Noto Sans Mono CJK SC" as a weak fallback to the monospace, sans-serif
and serif generic families.  A terminal that requests Terminus (or any other
Latin-only monospace font) therefore renders Chinese Wi-Fi SSIDs and other
CJK text instead of tofu, and kmscon can use the same face for the virtual
console.

Sans2.004 is the latest stable tag of the noto-cjk Sans line (the newer
Serif2.003 tags are a different family); the OFL-1.1 license text from the
release archive ships in the payload.

%prep
rm -rf noto-cjk
mkdir -p noto-cjk
python3 -c 'import sys, zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])' \
    %{SOURCE0} noto-cjk

%build

%install
rm -rf %{buildroot}
install -d -m 0755 %{buildroot}%{_datadir}/fonts/noto-cjk
install -m 0644 noto-cjk/NotoSansMonoCJKsc-Regular.otf \
    %{buildroot}%{_datadir}/fonts/noto-cjk/NotoSansMonoCJKsc-Regular.otf
install -m 0644 noto-cjk/NotoSansMonoCJKsc-Bold.otf \
    %{buildroot}%{_datadir}/fonts/noto-cjk/NotoSansMonoCJKsc-Bold.otf
install -d -m 0755 %{buildroot}%{_datadir}/doc/font-noto-cjk
install -m 0644 noto-cjk/LICENSE \
    %{buildroot}%{_datadir}/doc/font-noto-cjk/LICENSE
install -D -m 0644 %{_sourcedir}/69-tenko-noto-cjk.conf \
    %{buildroot}%{_sysconfdir}/fonts/conf.d/69-tenko-noto-cjk.conf

%files -f %{_sourcedir}/font-noto-cjk.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 2.004
- Package the Simplified Chinese monospace face (Noto Sans Mono CJK SC,
  Regular and Bold) from the latest stable Sans2.004 release, with a
  fontconfig fallback so Latin terminal fonts render Chinese instead of
  tofu.  The same face is the primary font for the kmscon console.
