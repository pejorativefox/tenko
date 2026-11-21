Name:       ripgrep
Version:    15.2.0
Release:    1
Summary:    Line-oriented search tool that recursively searches a regex pattern
License:    Unlicense OR MIT
URL:        https://github.com/BurntSushi/ripgrep
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
ExclusiveArch: x86_64

# Built from source with the distro rust toolchain.
BuildRequires: rust
BuildRequires: make-ca
# Optional feature, enabled so rg --pcre2 works (linked against the system pcre2)
BuildRequires: pcre2

%description
ripgrep (rg) recursively searches directories for a regex pattern while
respecting gitignore rules and skipping hidden files and binary files by
default.  It is faster than grep for large corpora and supports PCRE2-style
lookaround, multiline matching and structured output.

%prep
%setup -q

%build
export CARGO_HOME="$PWD/cargo-home"
export RUSTFLAGS="-C strip=symbols"
mkdir -p "$CARGO_HOME"
cargo build --locked --release -j4 --features pcre2

%install
rm -rf %{buildroot}
install -Dm755 target/release/rg %{buildroot}%{_bindir}/rg
install -d %{buildroot}%{_mandir}/man1 \
    %{buildroot}%{_datadir}/bash-completion/completions
target/release/rg --generate man > %{buildroot}%{_mandir}/man1/rg.1
target/release/rg --generate complete-bash \
    > %{buildroot}%{_datadir}/bash-completion/completions/rg
install -Dm644 LICENSE-MIT %{buildroot}%{_licensedir}/ripgrep/LICENSE-MIT
install -Dm644 COPYING %{buildroot}%{_licensedir}/ripgrep/COPYING

%files -f %{_sourcedir}/ripgrep.filelist

%changelog
* Fri Nov 20 2026 tenko <build@tenko.invalid> 15.2.0-1
- New package, not in the base set: latest upstream stable release
  (15.2.0, checked 2026-11-20).
