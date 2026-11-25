Name:       poppler-data
Version:    0.4.12
Release:    1
Summary:    CMap and encoding tables for poppler
License:    Adobe-2006 AND GPL-2.0-or-later AND MIT
URL:        https://poppler.freedesktop.org/
Source0:    poppler-data-%{version}.tar.gz
Prefix:     /usr

# BuildRequires: none (toolchain only)

%description
Encoding tables for poppler: the Adobe CMap resources needed to
render CJK PDFs, and the cidToUnicode, nameToUnicode and unicodeMap
tables from Glyph & Cog.  Consumers find it through the poppler-data
pkg-config entry; GIMP's PDF plug-in relies on it for non-embedded
CJK fonts.

%prep
%setup -q

%build
%make_build prefix=/usr

%install
rm -rf %{buildroot}
%make_install prefix=/usr

%files -f %{_sourcedir}/poppler-data.filelist

%changelog
* Wed Nov 25 2026 tenko <build@tenko.invalid> 0.4.12-1
- New package, not in the base set: latest upstream stable release
  (0.4.12, checked 2026-11-25); poppler needs it to render PDFs with
  CJK text, and through poppler GIMP's PDF plug-in.
- Data-only package: the Makefile installs the tables under
  /usr/share/poppler, with no code compiled.
