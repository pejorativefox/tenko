Name:       sound-theme-freedesktop
Version:    0.8
Release:    1
Summary:    Default freedesktop.org sound theme
License:    GPL-2.0-only AND GPL-2.0-or-later AND LGPL-2.0-or-later AND CC-BY-SA-3.0 AND CC-BY-3.0 AND CC-BY-4.0
URL:        https://www.freedesktop.org/wiki/Specifications/sound-theme-spec/
Prefix:     /usr
BuildArch:  noarch
Source0:    %{name}-%{version}.tar.gz

%description
The default freedesktop.org sound theme, implementing the Sound Theme
0.2 and Sound Naming 0.2 specifications.  It installs the event sounds
used by libcanberra (bell, dialog-error, dialog-warning, complete,
service-login and the other standard names) under
/usr/share/sounds/freedesktop.

%prep
# The GitLab archive keeps the repository name (xdg-sound-theme); the
# package still provides the freedesktop theme, so keep %{name} for the RPM.
%setup -q -n xdg-sound-theme-%{version}

%build
# Data-only package: nothing to compile.

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_datadir}/sounds/freedesktop/stereo
install -pm644 stereo/*.oga %{buildroot}%{_datadir}/sounds/freedesktop/stereo/

# Upstream 0.8 does not ship a dialog-error sample even though the Sound
# Naming 0.2 spec lists it as a standard alert and libcanberra does not
# fall back between event names.  Alias it to the warning sound so error
# dialogs (GTK_MESSAGE_ERROR -> dialog-error) are not silent (issue #43).
ln -s dialog-warning.oga \
    %{buildroot}%{_datadir}/sounds/freedesktop/stereo/dialog-error.oga

# Ship a static index.theme instead of running intltool over index.theme.in:
# the template's only translatable string is the display name, and the
# package is data-only.  The theme name is the directory name
# (freedesktop); keep the Name key in sync with it.  Directories=stereo
# selects the event-sound subdirectory.
install -pm644 %{_sourcedir}/index.theme \
    %{buildroot}%{_datadir}/sounds/freedesktop/index.theme

# The upstream COPYING file is empty; CREDITS carries the per-file licence
# and attribution notices, so ship it instead.
install -Dpm644 CREDITS %{buildroot}%{_licensedir}/%{name}/CREDITS
install -Dpm644 README %{buildroot}%{_docdir}/%{name}/README

%files -f %{_sourcedir}/%{name}.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 0.8-1
- New package: sound-theme-freedesktop 0.8, the latest stable upstream
  release (tag 0.8, 2012-09-25, linked from the Sound Theme specification).
  Data-only install with no compilation; provides
  /usr/share/sounds/freedesktop/index.theme (Directories=stereo) and the
  event sounds for libcanberra (issue #43).
- Source is the upstream GitLab 0.8 tag archive.  The
  people.freedesktop.org 0.8 tarball omits five sounds that are present in
  the 0.8 tag (network-connectivity-established/lost, power-plug,
  power-unplug, screen-capture), so the tag archive is the complete release.
- Add stereo/dialog-error.oga as a symlink to dialog-warning.oga: upstream
  0.8 has no error sample, the Sound Naming 0.2 spec lists dialog-error as
  a standard alert, and libcanberra does not fall back between event names.
