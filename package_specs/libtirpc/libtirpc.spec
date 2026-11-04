Name:       libtirpc
Version:    1.3.8
Release:    2
Summary:    Transport-independent RPC library
License:    BSD
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2

%description
libtirpc is the transport-independent Sun RPC implementation used by Xorg.

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

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.3.8-2
- Rebuild for the base repo; required by iproute2 (size audit P0)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.3.7-1
- Initial package (BLFS r13.1)
