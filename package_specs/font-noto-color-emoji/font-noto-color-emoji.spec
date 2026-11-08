# Noto Color Emoji is the color emoji face from the Noto project (the COLRv1
# build published through Google Fonts).  It is desktop-only: kmscon's
# freetype backend renders 8-bit coverage bitmaps and cannot blit the color
# bitmap, so the base system installs the monochrome font-noto-emoji instead.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       font-noto-color-emoji
Version:    2.055
Release:    1
Summary:    Noto Color Emoji
License:    OFL-1.1
URL:        https://github.com/googlefonts/noto-emoji
Prefix:     /usr
Source0:    NotoColorEmoji-Regular.ttf
Source1:    notocoloremoji-OFL.txt

ExclusiveArch: x86_64

AutoProv: no
AutoReq: no

%description
Noto Color Emoji is the color emoji face from the Noto project.  It is the
COLRv1 build published through Google Fonts (the same face as the noto-emoji
project's Noto-COLRv1.ttf) and provides the full Unicode emoji repertoire for
GUI applications and the desktop terminal.

The base system keeps the monochrome font-noto-emoji face for kmscon; this
package is pulled in by the desktop metas so XFCE and GUI toolkits get color
emoji.  The fontconfig snippet appends the face as a weak fallback for the
generic families, after the monochrome face, so a monospace pattern can still
resolve color emoji in a graphical terminal.

Version 2.055 is the font table version of the current Google Fonts build.
OFL-1.1 text ships in the payload.

%prep

%build

%install
rm -rf %{buildroot}
install -d -m 0755 %{buildroot}%{_datadir}/fonts/noto-color-emoji
install -m 0644 %{SOURCE0} \
    %{buildroot}%{_datadir}/fonts/noto-color-emoji/NotoColorEmoji-Regular.ttf
install -d -m 0755 %{buildroot}%{_datadir}/doc/font-noto-color-emoji
install -m 0644 %{SOURCE1} \
    %{buildroot}%{_datadir}/doc/font-noto-color-emoji/OFL.txt
install -D -m 0644 %{_sourcedir}/69-tenko-noto-color-emoji.conf \
    %{buildroot}%{_sysconfdir}/fonts/conf.d/69-tenko-noto-color-emoji.conf

%files -f %{_sourcedir}/font-noto-color-emoji.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 2.055
- Package the current Google Fonts Noto Color Emoji COLRv1 build as the
  desktop color emoji face; the base system keeps the monochrome
  font-noto-emoji face for kmscon.
