Name:       rust
Version:    1.100.0
Release:    2
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

# The installed rust was built with libdir = lib64, so its rustc looks for
# the standard library in <sysroot>/lib64/rustlib/<target>/lib; x.py keeps
# stage0's in <sysroot>/lib/rustlib/<target>/lib (in the snapshot sysroot
# and in its own build/<target>/stage0-sysroot, where it also creates an
# empty lib64 one).  Run stage0 through a wrapper that points the lib64
# directory of a stage0 sysroot at the lib one, and defaults the sysroot to
# ./stage0.  The target libraries are copied, not linked: x.py copies them
# into its stage0-sysroot and fails on symlinks.
mkdir -p stage0/bin stage0/lib/rustlib
cp -a %{_libdir}/rustlib/x86_64-unknown-linux-gnu stage0/lib/rustlib/
cat > stage0/bin/rustc <<EOF
#!/bin/sh
sysroot= next=
for arg; do
    if [ -n "\$next" ]; then sysroot=\$arg; next=; continue; fi
    case \$arg in
        --sysroot) next=1 ;;
        --sysroot=*) sysroot=\${arg#--sysroot=} ;;
    esac
done
if [ -z "\$sysroot" ]; then
    sysroot=$PWD/stage0
    set -- --sysroot "\$sysroot" "\$@"
fi
case \$sysroot in
    $PWD/stage0|*/stage0-sysroot)
        src=\$sysroot/lib/rustlib/x86_64-unknown-linux-gnu/lib
        dst=\$sysroot/lib64/rustlib/x86_64-unknown-linux-gnu/lib
        if [ -d "\$src" ] && [ ! -L "\$dst" ] &&
           [ -z "\$(ls -A "\$dst" 2>/dev/null)" ]; then
            mkdir -p "\${dst%%/lib}"
            rmdir "\$dst" 2>/dev/null
            ln -sfn "\$src" "\$dst"
        fi ;;
esac
exec %{_bindir}/rustc "\$@"
EOF
chmod 755 stage0/bin/rustc

cat > bootstrap.toml <<EOF
change-id = "ignore"
profile = "dist"

[llvm]
link-shared = true

[build]
build = "x86_64-unknown-linux-gnu"
host = ["x86_64-unknown-linux-gnu"]
target = ["x86_64-unknown-linux-gnu"]
rustc = "$PWD/stage0/bin/rustc"
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
# A same-version stage0 leaves lint expectations written for beta unfulfilled.
deny-warnings = false

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

# librustc_driver's file name carries a hash of the compiler version string
# (which includes the release and depends on the stage0 compiler), so it is
# listed here, exactly one file, instead of in the static filelist.
ls %{buildroot}%{_libdir}/librustc_driver-*.so | sed 's#^%{buildroot}##' > rust-driver.filelist
test "$(wc -l < rust-driver.filelist)" = 1

%check
# The freshly installed compiler must report itself and build, link (with
# the default linker settings: cc and the system ld, since rust-lld is not
# shipped) and run a program against its own standard library.
export LD_LIBRARY_PATH=%{buildroot}%{_libdir}
%{buildroot}%{_bindir}/rustc --version --verbose
printf 'fn main() { println!("hello from rustc"); }\n' > t.rs
%{buildroot}%{_bindir}/rustc --sysroot %{buildroot}%{_prefix} -o t t.rs
./t

%files -f %{_sourcedir}/rust.filelist -f rust-driver.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 1.100.0-2
- Rebuild from the installed rust 1.100.0 (#58): run stage0 through a
  rustc wrapper that finds its standard library in x.py's lib/rustlib
  sysroots (the installed rustc looks in lib64/rustlib), and turn off
  rust.deny-warnings, since a same-version stage0 leaves lint expectations
  written for beta unfulfilled.
- List librustc_driver-<hash>.so from %%install: the hash follows the
  compiler version string and the stage0 compiler.

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
