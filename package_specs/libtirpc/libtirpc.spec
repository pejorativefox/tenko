Name:       libtirpc
Version:    1.3.7
Release:    1
Summary:    Transport-independent RPC library
License:    BSD
Prefix:     /usr
Source0:    libtirpc-1.3.7.tar.bz2

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
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.3.7-1
- Initial package (BLFS r13.1)
