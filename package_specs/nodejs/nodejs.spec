# Official Node.js prebuilt linux-x64 distribution, installed under /opt.
# The source-built package was replaced at the user's request; this keeps the
# upstream binary (including npm) exactly as released.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       nodejs
Version:    26.13.0
Release:    2
Summary:    JavaScript runtime built on Chrome's V8 JavaScript engine (binary distribution)
License:    MIT
URL:        https://nodejs.org/
Source0:    node-v%{version}-linux-x64.tar.xz

ExclusiveArch: x86_64

# The released binary links the system C/C++ runtime; RPM auto-requires add
# the correct sonames (glibc, libstdc++, libgcc_s).
Provides:   npm = 11.20.0
Requires:   ca-certificates

%description
Node.js is a JavaScript runtime built on Chrome's V8 JavaScript engine.
This package installs the official upstream linux-x64 binary distribution
under /opt/node-v26.13.0-linux-x64 (with /opt/node as a stable symlink) and
provides node, npm, npx, and corepack in /usr/bin.

It is not a source build: the binaries, bundled OpenSSL, ICU, and npm are
exactly the ones published by nodejs.org.

%prep
%setup -q -n node-v%{version}-linux-x64

%build

%install
rm -rf %{buildroot}
install -d %{buildroot}/opt/node-v%{version}-linux-x64 %{buildroot}/usr/bin
cp -a . %{buildroot}/opt/node-v%{version}-linux-x64/
ln -s node-v%{version}-linux-x64 %{buildroot}/opt/node
for b in node npm npx corepack; do
    if [ -e "%{buildroot}/opt/node/bin/$b" ]; then
        ln -s "/opt/node/bin/$b" "%{buildroot}/usr/bin/$b"
    fi
done

%files -f %{_sourcedir}/nodejs.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 26.13.0-2
- Replace the source build with the official nodejs.org linux-x64 binary
  distribution installed under /opt, as requested.
- /opt/node-v26.13.0-linux-x64 plus /opt/node symlink; node/npm/npx in
  /usr/bin.  Bundled npm is 11.20.0.
- Node 26.13.0 remains the user-approved LTS exception to 26.9.0
  pin.
