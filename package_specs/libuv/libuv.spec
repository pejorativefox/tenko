Name:       libuv
Version:    1.53.0
Release:    3
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-v%{version}.tar.gz

%description
TODO

%prep
%setup -q -n libuv-v%{version}

%build
sh autogen.sh
%configure --disable-static
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libuv.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.53.0-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

# let's skip this for now
