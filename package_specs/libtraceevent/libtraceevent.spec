Name:       libtraceevent
Version:    1.9.1
Release:    1
Summary:    Library to parse raw trace event formats
License:    LGPL-2.1-only AND LGPL-2.1-or-later AND GPL-2.0-only AND GPL-2.0-or-later
URL:        https://git.kernel.org/pub/scm/libs/libtrace/libtraceevent.git/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: meson
BuildRequires: ninja
BuildRequires: gcc

%description
libtraceevent provides a library for parsing the raw event data exposed by
the Linux kernel tracing infrastructure.  It is used by trace-cmd, perf,
PowerTOP and other tracing and profiling tools.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup --prefix=/usr --buildtype=release \
    -Ddefault_library=shared -Ddoc=false ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libtraceevent.filelist

%changelog
* Wed Nov 11 2026 browneye <build@browneye.invalid> 1.9.1-1
- New package: libtraceevent 1.9.1 (latest stable upstream).  It is not
  in the base set; PowerTOP requires libtracefs, which requires this
  library.
- Source: https://git.kernel.org/pub/scm/libs/libtrace/libtraceevent.git/snapshot/libtraceevent-1.9.1.tar.gz
  md5 0b679474de789930a06591a97a4823ee
  sha256 3bc19dd940914260ba591b5276723bf84bb43f82c7c3d4267622bee4d016ea55
- Build the shared library and the event-format plugins; documentation
  is disabled because the build image does not carry asciidoc/xmlto.
