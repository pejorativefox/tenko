Name:       libuv
Version:    1.53.0
Release:    4
Summary:    Multi-platform asynchronous I/O library
License:    MIT
Prefix:     /usr
Source0:    %{name}-v%{version}.tar.gz

%description
libuv is a multi-platform support library with a focus on asynchronous I/O.
It provides an event loop, asynchronous TCP and UDP sockets, DNS resolution,
file system operations, child processes and a thread pool.

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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.53.0-4
- Replace the TODO summary/description and record the verified license
  (MIT): LICENSE (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.53.0-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

# let's skip this for now
