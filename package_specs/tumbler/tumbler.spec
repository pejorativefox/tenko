Name:       tumbler
Version:    4.20.2
Release:    4
Summary:    D-Bus service for applications to request thumbnails
License:    GPL-2.0-or-later AND LGPL-2.0-or-later
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
D-Bus service for applications to request thumbnails

%prep
%setup

%build
%configure --disable-gstreamer-thumbnailer
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install
rm -f %{buildroot}/usr/lib/systemd/user/tumblerd.service

%files -f %{_sourcedir}/tumbler.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.2-4
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later AND LGPL-2.0-or-later): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.2-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).
- Disable the GStreamer thumbnailer explicitly.  The build image ships
  the GStreamer headers, while the image the published package was built
  in did not, so autodetection added tumbler-gst-thumbnailer.so.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.2-2
- Split devel payload into tumbler-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.2
- Sync with 4.19.0

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.2.7
- Initial RPM

