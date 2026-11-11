Name:       libtracefs
Version:    1.8.4
Release:    1
Summary:    Library for accessing the kernel tracefs filesystem
License:    LGPL-2.1-or-later AND GPL-2.0-or-later AND GPL-2.0-only
URL:        https://git.kernel.org/pub/scm/libs/libtrace/libtracefs.git/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: meson
BuildRequires: ninja
BuildRequires: gcc
BuildRequires: flex
BuildRequires: bison
BuildRequires: libtraceevent

%description
libtracefs provides a library for accessing the Linux kernel tracefs
filesystem.  It creates and manages tracing instances, events, filters,
kprobes, uprobes, histograms and synthetic events, and it can read and
write the trace buffers.  PowerTOP uses it to collect wakeup and process
activity data.

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

%files -f %{_sourcedir}/libtracefs.filelist

%changelog
* Wed Nov 11 2026 browneye <build@browneye.invalid> 1.8.4-1
- New package: libtracefs 1.8.4 (latest stable upstream).  It is not in
  the base set; PowerTOP requires it for tracefs access.
- Source: https://git.kernel.org/pub/scm/libs/libtrace/libtracefs.git/snapshot/libtracefs-1.8.4.tar.gz
  md5 0ffb21d2bb690d83d619481e02652d7a
  sha256 75187bad93e622c94c4a691173e45f08948d38b9a28e9b855b54a3e956d289a6
- Requires libtraceevent >= 1.8.1 (packaged separately).
- Build the shared library and the sqlhist utility; documentation is
  disabled because the build image does not carry asciidoc/xmlto.
