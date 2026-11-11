# Official Rust binary distribution, installed under /opt.  This is not a
# source build: rustc/cargo/rustdoc/rustfmt/clippy/rust-analyzer are the
# published upstream binaries.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       rust
Version:    1.99.0
Release:    1
Summary:    Rust programming language toolchain (official binary distribution)
License:    MIT OR Apache-2.0
URL:        https://www.rust-lang.org/
Source0:    rust-%{version}-x86_64-unknown-linux-gnu.tar.gz

ExclusiveArch: x86_64

Provides:   cargo = %{version}
Provides:   rustc = %{version}
Requires:   gcc
Requires:   ca-certificates

%description
The Rust programming language toolchain, installed from the official
rust-1.99.0-x86_64-unknown-linux-gnu binary distribution.

The toolchain lives under /opt/rust-1.99.0-x86_64-unknown-linux-gnu
(with /opt/rust as a stable symlink).  rustc, cargo, rustdoc, rustfmt,
clippy, and rust-analyzer are linked into /usr/bin.

tenko.lock pins Rust 1.98.1; this is the newer upstream stable release.

%prep
%setup -q -n rust-%{version}-x86_64-unknown-linux-gnu

%build

%install
rm -rf %{buildroot}
./install.sh \
    --prefix=/opt/rust-%{version}-x86_64-unknown-linux-gnu \
    --destdir=%{buildroot} \
    --disable-ldconfig

ln -s rust-%{version}-x86_64-unknown-linux-gnu %{buildroot}/opt/rust
install -d %{buildroot}/usr/bin
for b in rustc cargo rustdoc rustfmt cargo-clippy cargo-fmt clippy-driver \
         rust-analyzer rust-gdb rust-gdbgui rust-lldb; do
    if [ -e "%{buildroot}/opt/rust/bin/$b" ]; then
        ln -s "/opt/rust/bin/$b" "%{buildroot}/usr/bin/$b"
    fi
done

%files -f %{_sourcedir}/rust.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.99.0-1
- New package: official rust-1.99.0-x86_64-unknown-linux-gnu binary
  distribution installed under /opt, with /opt/rust and /usr/bin symlinks.
  User-requested binary packaging (not a source build).
