# GNU Unifont ships as ready-made artifacts from unifoundry.com (PCF for the
# GRUB boot font and OpenType outline coverage of the Unicode base plane,
# supplementary planes and CSUR).  The payload is preserved exactly as
# released: no strip, no re-pack, AutoProv/AutoReq off.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       font-ttf-unifont
Version:    17.0.03
Release:    1
Summary:    GNU Unifont: bitmap+outline coverage of the Unicode code points
License:    OFL
Prefix:     /usr
Source0:    unifont-%{version}.otf
Source1:    unifont_upper-%{version}.otf
Source2:    unifont_csur-%{version}.otf
Source3:    unifont-%{version}.pcf.gz

ExclusiveArch: x86_64

AutoProv: no
AutoReq: no

%description
GNU Unifont is the "Unicode base font": one bitmap glyph for every Unicode
code point (via otfform outlines rendered from the double-struck−style
bitmap), with the supplementary planes in unifont_upper and the CSUR
(Canadian Aboriginal syllabics-etc) block in unifont_csur.  It also ships
the 8x16 PCF used by GRUB as the boot font.

The Unifont package page is archived (only the PCF has an up-to-date
entity); the user explicitly requested packaging the unicode symbol font,
so the current 17.0.03 artifacts are shipped as a user-approved exception
to the Tenko version-policy rule.  License: OFL for the OTF
artifacts; GPL+FE for the bitmap glyphs held in the PCF.

%install
rm -rf %{buildroot}
install -d -m 0755 %{buildroot}/usr/share/fonts/unifont
install -m 0644 %{SOURCE0} %{buildroot}/usr/share/fonts/unifont/unifont-%{version}.otf
install -m 0644 %{SOURCE1} %{buildroot}/usr/share/fonts/unifont/unifont_upper-%{version}.otf
install -m 0644 %{SOURCE2} %{buildroot}/usr/share/fonts/unifont/unifont_csur-%{version}.otf
install -m 0644 %{SOURCE3} %{buildroot}/usr/share/fonts/unifont/unifont-%{version}.pcf.gz

%files -f %{_sourcedir}/font-ttf-unifont.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 17.0.03
- Package the unicode symbol font: unifont 17.0.03 otf (base plane, upper
  planes, CSUR) plus the GRUB boot PCF from the pinned entity
- Binary font package; user-approved exception (page is archived)
