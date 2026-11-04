Name:       libfyaml
Version:    0.9.6
Release:    3
Summary:    Fully feature complete YAML parser and emitter
License:    MIT
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
libfyaml is a YAML 1.2 parser and emitter library.  AppStream requires it to
read its YAML metadata catalogues.

%package devel
Summary:    Development files for libfyaml
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in libfyaml; this empty package only
exists so upgrades from the split layout resolve without a file
conflict.

%prep
%setup -q

%build
%configure --disable-static --without-libclang
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libfyaml.filelist
%files devel

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.9.6-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.9.6-1
- New package, synced with BLFS r13.1.  Required by AppStream.
