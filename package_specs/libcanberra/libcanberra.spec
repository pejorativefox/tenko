Name:       libcanberra
Version:    0.30
Release:    3
Summary:    libcanberra is an implementation of the XDG Sound Theme and Name Specifications
License:    GPL
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
libcanberra is an implementation of the XDG Sound Theme and Name Specifications

%prep
%setup

%build
%configure --disable-oss --disable-alsa --disable-gstreamer
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libcanberra.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.30-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).
- Disable the ALSA and GStreamer backends explicitly.  The build image
  ships their headers, while the image the published package was built
  in did not, so autodetection would add the plugins and a GStreamer
  runtime dependency.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.30-2
- Split devel payload into libcanberra-devel (size audit)

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 0.30
- Initial RPM

