Name:       arc-theme
Version:    20221218
Release:    1
Summary:    Flat theme with transparent elements for GTK and Xfce
License:    GPL-3.0-only
URL:        https://github.com/gooroom/arc-theme
Prefix:     /usr
BuildArch:  noarch
Source0:    arc-theme-gooroom-%{version}-1-grm4u1.tar.gz
Source1:    arc-theme-%{version}.tar.xz

BuildRequires: meson
BuildRequires: ninja
BuildRequires: sassc
BuildRequires: glib

%description
Arc is a flat theme with transparent elements for GTK 2, GTK 3, GTK 4
and various desktop shells and window managers, including Xfce
(xfwm4), Metacity, Plank and Unity.

This package follows the Gooroom fork of Arc (gooroom-4.0), which keeps
the theme working with current toolkits.  It builds the four Arc,
Arc-Darker, Arc-Dark and Arc-Lighter variants.

%prep
%setup -q -n arc-theme-gooroom-%{version}-1-grm4u1 -a 1

# The Gooroom tag archive is a git snapshot and does not include the PNG
# assets that 'meson dist' renders with Inkscape.  The upstream 20221218
# release tarball is the matching Meson dist for this fork; copy its
# pre-rendered assets so the build does not need Inkscape.
for png in $(cd arc-theme-%{version} && find common -name '*.png'); do
    [ -e "$png" ] || install -Dpm644 "arc-theme-%{version}/$png" "$png"
done

%build
meson setup build \
      --prefix=/usr \
      --buildtype=release \
      -D themes=gtk2,gtk3,gtk4,metacity,plank,unity,xfwm \
      -D variants=light,darker,dark,lighter
ninja -C build

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install
install -Dpm644 COPYING %{buildroot}%{_licensedir}/arc-theme/COPYING

%files -f %{_sourcedir}/arc-theme.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 20221218-1
- New package: Gooroom fork of Arc (gooroom-4.0, tag
  gooroom/20221218-1+grm4u1), based on upstream jnsh/arc-theme
  20221218.  The matching upstream Meson dist supplies the pre-rendered
  PNG assets, so no Inkscape build dependency is needed.
