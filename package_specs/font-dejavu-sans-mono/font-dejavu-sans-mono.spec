# DejaVu Sans Mono is the monospaced member of the DejaVu family (Bitstream
# Vera outline with the Arev additions).  Tenko uses it as the cell-aligned
# symbol fallback: it covers the Dingbats, Miscellaneous Symbols and
# Geometric Shapes ranges that Terminus and the Nerd Fonts symbol faces do
# not, so a TUI that draws characters such as U+2731, U+2610, U+2612, U+25B0
# or U+25D1 gets them at one cell instead of tofu or a double-width CJK
# glyph.  Payload is preserved as released: no strip, AutoProv/AutoReq off.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       font-dejavu-sans-mono
Version:    2.37
Release:    1
Summary:    DejaVu Sans Mono: monospaced outline font with symbol coverage
License:    Bitstream-Vera
URL:        https://dejavu-fonts.github.io/
Prefix:     /usr
Source0:    dejavu-fonts-ttf-2.37.tar.bz2

ExclusiveArch: x86_64

AutoProv: no
AutoReq: no

%description
DejaVu Sans Mono is a monospaced TrueType face derived from Bitstream Vera,
with the Arev glyph additions.  Besides a full Latin/Greek/Cyrillic
repertoire it covers the Dingbats, Miscellaneous Symbols and Geometric
Shapes blocks, which the Base fonts (Terminus, Noto CJK, Noto Emoji and
Symbols Nerd Font Mono) leave empty.

The package installs the Regular, Bold, Oblique and Bold-Oblique faces and a
fontconfig snippet that appends "DejaVu Sans Mono" weakly after the
requested text font but ahead of the CJK and emoji fallbacks.  Latin text
therefore keeps the user's terminal font while symbols such as the ones
opencode and other TUIs draw for spinners, check boxes and progress bars
keep a single terminal cell.

2.37 is the latest stable DejaVu release (the project has not tagged a newer
one); the Bitstream Vera license text from the release archive ships in the
payload.

%prep
rm -rf dejavu-fonts-ttf-%{version}
tar -xjf %{SOURCE0}

%build

%install
rm -rf %{buildroot}
install -d -m 0755 %{buildroot}%{_datadir}/fonts/dejavu-sans-mono
for face in DejaVuSansMono DejaVuSansMono-Bold \
            DejaVuSansMono-Oblique DejaVuSansMono-BoldOblique; do
    install -m 0644 dejavu-fonts-ttf-%{version}/ttf/$face.ttf \
        %{buildroot}%{_datadir}/fonts/dejavu-sans-mono/$face.ttf
done
install -d -m 0755 %{buildroot}%{_datadir}/doc/font-dejavu-sans-mono
install -m 0644 dejavu-fonts-ttf-%{version}/LICENSE \
    %{buildroot}%{_datadir}/doc/font-dejavu-sans-mono/LICENSE
install -D -m 0644 %{_sourcedir}/69-tenko-dejavu-sans-mono.conf \
    %{buildroot}%{_sysconfdir}/fonts/conf.d/69-tenko-dejavu-sans-mono.conf

%files -f %{_sourcedir}/font-dejavu-sans-mono.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 2.37
- Package the DejaVu Sans Mono faces (Regular, Bold, Oblique, Bold-Oblique)
  and make the family a weak monospace fallback ahead of the CJK and emoji
  faces.  Terminus, Noto CJK, Noto Emoji and Symbols Nerd Font Mono have no
  glyphs for the Dingbats/Miscellaneous Symbols/Geometric Shapes characters
  that TUIs use for spinners, check boxes and progress bars (U+2731, U+2737,
  U+2738, U+2610, U+2612, U+25B0, U+25D1); fontconfig fell back to Luxi Mono
  (also empty, so tofu) or to the double-width Noto CJK face (misaligned
  rows).  DejaVu Sans Mono covers them at one cell.  2.37 is the latest
  stable upstream release.
