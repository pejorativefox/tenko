Name:       rust
Version:    1.100.0
Release:    1
Summary:    The Rust programming language toolchain
License:    (Apache-2.0 OR MIT) AND (Artistic-2.0 AND BSD-3-Clause AND ISC AND MIT AND Unicode-DFS-2016) AND (Apache-2.0 WITH LLVM-exception)
URL:        https://www.rust-lang.org/
Source0:    rustc-%{version}-src.tar.xz
Prefix:     /usr
ExclusiveArch: x86_64

Provides:   cargo = %{version}-%{release}
Provides:   rustc = %{version}-%{release}
Requires:   gcc
Requires:   ca-certificates

# rustc is written in Rust: x.py needs the previous stable release
# (src/stage0 compiler_version, 1.99.0 for 1.100.0).  The installed rust is
# that bootstrap, so each release is built by the previous one.  rustc links
# the system LLVM (llvm-devel, LLVM >= 21) instead of building the bundled
# fork; the crates the toolchain needs are vendored in the source tarball.
BuildRequires: rust
BuildRequires: llvm-devel
BuildRequires: python
BuildRequires: cmake
BuildRequires: ninja
BuildRequires: pkgconf
BuildRequires: openssl
BuildRequires: zlib
BuildRequires: curl
BuildRequires: libssh2
BuildRequires: xz
BuildRequires: zstd

%description
The Rust programming language toolchain built from the upstream source
release: rustc, cargo, rustdoc, rustfmt, clippy, rust-analyzer and the
standard library source (rust-src) for x86_64-unknown-linux-gnu.

%prep
%setup -q -n rustc-%{version}-src

cat > bootstrap.toml <<EOF
change-id = "ignore"
profile = "dist"

[llvm]
link-shared = true

[build]
build = "x86_64-unknown-linux-gnu"
host = ["x86_64-unknown-linux-gnu"]
target = ["x86_64-unknown-linux-gnu"]
rustc = "/usr/bin/rustc"
cargo = "/usr/bin/cargo"
docs = false
extended = true
tools = ["cargo", "clippy", "rustdoc", "rustfmt", "rust-analyzer", "rust-src"]
description = "Tenko %{version}-%{release}"
vendor = true
locked-deps = true
jobs = %{_smp_build_ncpus}

[install]
prefix = "%{_prefix}"
sysconfdir = "%{_sysconfdir}"
libdir = "lib64"
mandir = "share/man"
docdir = "share/doc/rust"

[rust]
channel = "stable"
rpath = false
lld = false
llvm-tools = false
codegen-units-std = 1
debuginfo-level = 0
remap-debuginfo = true
download-rustc = false

[target.x86_64-unknown-linux-gnu]
llvm-config = "/usr/bin/llvm-config"
cc = "gcc"
cxx = "g++"
linker = "gcc"
# Link through cc and the system linker; rust-lld is not built.
default-linker-linux-override = "off"
EOF

%build
export RUSTFLAGS= CARGO_HOME="$PWD/cargo-home"
python3 x.py build

%install
rm -rf %{buildroot}
export RUSTFLAGS= CARGO_HOME="$PWD/cargo-home"
DESTDIR=%{buildroot} python3 x.py install

# Installer bookkeeping that rpm owns instead.
for f in install.log uninstall.sh rust-installer-version components; do
    rm -f %{buildroot}%{_libdir}/rustlib/$f
done
rm -f %{buildroot}%{_libdir}/rustlib/manifest-*
# Each component's installer rewrites the shared README/LICENSE files and
# keeps the previous copy as *.old.
rm -f %{buildroot}%{_docdir}/rust/*.old
# A JSON schema for custom target specs: documentation, not configuration.
mv %{buildroot}%{_sysconfdir}/target-spec-json-schema.json %{buildroot}%{_docdir}/rust/

%check
# The freshly installed compiler must report itself and build, link (with
# the default linker settings: cc and the system ld, since rust-lld is not
# shipped) and run a program against its own standard library.
export LD_LIBRARY_PATH=%{buildroot}%{_libdir}
%{buildroot}%{_bindir}/rustc --version --verbose
printf 'fn main() { println!("hello from rustc"); }\n' > t.rs
%{buildroot}%{_bindir}/rustc --sysroot %{buildroot}%{_prefix} -o t t.rs
./t

%files -f %{_sourcedir}/rust.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 1.100.0-1
- Build the toolchain from the upstream source release instead of
  repackaging the binary distribution under /opt.  1.100.0 is the latest
  upstream stable (released 2026-11-09, checked 2026-11-14).  Installed
  under /usr (libraries and rustlib in /usr/lib64); links the system
  LLVM 23.  Bootstrapped from the installed rust 1.99.0.
- Ships rustc, cargo, rustdoc, rustfmt, clippy, rust-analyzer, rust-src
  and the rust-gdb/rust-lldb wrappers.  The HTML documentation and
  rust-lld are not built; rustc links through cc and the system ld.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.99.0-1
- New package: official rust-1.99.0-x86_64-unknown-linux-gnu binary
  distribution installed under /opt, with /opt/rust and /usr/bin symlinks.
  User-requested binary packaging (not a source build).
