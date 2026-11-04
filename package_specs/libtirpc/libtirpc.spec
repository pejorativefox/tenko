Name:       libtirpc
Version:    1.3.8
Release:    4
Summary:    Transport-independent RPC library
License:    BSD
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2

%description
libtirpc is the transport-independent Sun RPC implementation used by Xorg.

%package devel
Summary:    Development files for libtirpc
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in libtirpc; this empty package only
exists so upgrades from the split layout resolve without a file
conflict.

%prep
%setup -q

%build
%configure --disable-static --disable-gssapi
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libtirpc.filelist
%files devel

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.3.8-4
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.3.8-2
- Rebuild for the base repo; required by iproute2 (size audit P0)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.3.7-1
- Initial package (BLFS r13.1)
