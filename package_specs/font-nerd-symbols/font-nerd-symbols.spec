# Symbols-only Nerd Font: the fontconfig-style fallback face that provides
# Nerd Fonts icons (Powerline, Font Awesome, Material Design, Octicons, ...)
# without patching the user's primary terminal font.  Upstream publishes it
# as a release archive with both a proportional and a monospace face; the
# monospace face is used for terminals and kmscon so icons keep the cell grid.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       font-nerd-symbols
Version:    3.5.1
Release:    1
Summary:    Nerd Fonts symbols (proportional and monospace fallback faces)
License:    MIT AND CC-BY-4.0 AND Apache-2.0 AND OFL-1.1
URL:        https://github.com/ryanoasis/nerd-fonts
Prefix:     /usr
Source0:    NerdFontsSymbolsOnly.tar.xz

ExclusiveArch: x86_64

AutoProv: no
AutoReq: no

%description
This package ships the "Symbols Nerd Font" and "Symbols Nerd Font Mono"
faces from the Nerd Fonts release archive.  They contain the icon ranges
(Powerline, Font Awesome, Material Design, Octicons, Devicons, Weather
Icons, ...) and are intended to be selected through fontconfig as a fallback
next to a normal text font, so the terminal font does not need to be patched.

The package does not ship the upstream "monospace prefers Symbols Nerd Font"
fontconfig file: that replaces the primary monospace family instead of
appending a fallback.  Tenko's snippet appends the symbol faces weakly after
the requested family.

The upstream README lists the individual icon-set licenses (MIT, CC BY 4.0,
Apache-2.0 and OFL-1.1); the combined SPDX expression reflects that set.

%prep

%build

%install
rm -rf %{buildroot}
tmp=$(mktemp -d)
tar -xJf %{SOURCE0} -C "$tmp"
install -d -m 0755 %{buildroot}%{_datadir}/fonts/nerd-symbols
install -m 0644 "$tmp/SymbolsNerdFont-Regular.ttf" \
    %{buildroot}%{_datadir}/fonts/nerd-symbols/SymbolsNerdFont-Regular.ttf
install -m 0644 "$tmp/SymbolsNerdFontMono-Regular.ttf" \
    %{buildroot}%{_datadir}/fonts/nerd-symbols/SymbolsNerdFontMono-Regular.ttf
install -d -m 0755 %{buildroot}%{_datadir}/doc/font-nerd-symbols
install -m 0644 "$tmp/LICENSE" \
    %{buildroot}%{_datadir}/doc/font-nerd-symbols/LICENSE
install -m 0644 "$tmp/README.md" \
    %{buildroot}%{_datadir}/doc/font-nerd-symbols/README.md
rm -rf "$tmp"
install -D -m 0644 %{_sourcedir}/69-tenko-nerd-symbols.conf \
    %{buildroot}%{_sysconfdir}/fonts/conf.d/69-tenko-nerd-symbols.conf

%files -f %{_sourcedir}/font-nerd-symbols.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 3.5.1
- Package the symbols-only Nerd Fonts v3.5.1 archive (proportional and
  monospace faces) as a weak generic-family fallback, so terminals and the
  kmscon console render Nerd Font icons without patching the text font.
