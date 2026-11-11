Name:       libopus
Version:    1.6.1
Release:    1
Summary:    Audio compression format
License:    BSD-3-Clause
URL:        https://github.com/xiph/opus
Prefix:     /usr
Source0:    opus-%{version}.tar.gz

BuildRequires: meson, ninja

%description
Opus is a lossy audio compression format developed by the Internet
Engineering Task Force (IETF) that is particularly suitable for
interactive speech and audio transmission over the Internet.  This
package provides the Opus library and headers.

%prep
%setup -q -n opus-%{version}

%build
mkdir build
pushd build
meson setup --prefix=/usr                                \
            --buildtype=release                          \
            -D docdir=/usr/share/doc/opus-%{version}     \
            ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libopus.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.6.1-1
- Update to 1.6.1, the pinned version
  (multimedia/libdriv/opus.xml).
- Build with meson as the base build does, with the documented docdir.
- First Browneye build; replaces the stale 1.3 spec.
