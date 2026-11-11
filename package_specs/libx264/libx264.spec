Name:       libx264
Version:    20250815
Release:    1
Summary:    H.264/MPEG-4 AVC video encoder library
License:    GPL-2.0-or-later
URL:        https://www.videolan.org/developers/x264.html
Source0:    x264-%{version}.tar.xz
Prefix:     /usr

BuildRequires: nasm

%description
x264 provides a library for encoding video streams into the
H.264/MPEG-4 AVC format.

%prep
%setup -q -n x264-%{version}

%build
./configure --prefix=/usr      \
            --libdir=%{_libdir} \
            --enable-shared    \
            --disable-cli
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libx264.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 20250815-1
- Update to the pinned snapshot 20250815
  (multimedia/libdriv/x264.xml).
- Use the documented configure flags (--enable-shared --disable-cli) and
  pass --libdir=%{_libdir} so the library lands in /usr/lib64.
- Fix the old spec's "--diasble-cli" typo, which made it build the
  command-line encoder.
- nasm is the only assembly dependency (recommended); the
  spec does not require yasm.
