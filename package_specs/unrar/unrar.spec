Name:       unrar
Version:    7.2.7
Release:    1
Summary:    Extractor for RAR archives
License:    UnRAR
URL:        https://www.rarlab.com/rar_add.htm
Prefix:     /usr
Source0:    unrarsrc-%{version}.tar.gz

# BuildRequires: none (toolchain only)

%description
UnRAR is the official freeware extractor for RAR archives from RARLAB.
It lists, tests and extracts RAR 5 and legacy RAR 4 archives, including
multi-volume and password-protected ones.  It cannot create RAR
archives: the RAR compression algorithm is proprietary, and the UnRAR
license forbids using this source to re-create it.

%prep
%setup -q -n unrar

%build
# The upstream makefile hardcodes its own CXXFLAGS; keep its warning
# suppressions and -std=c++11, but compile with the distro optflags.
%make_build CXXFLAGS="%{optflags} -std=c++11 -Wno-logical-op-parentheses -Wno-switch -Wno-dangling-else"

%install
rm -rf %{buildroot}
install -Dm755 unrar %{buildroot}%{_bindir}/unrar
install -Dm644 license.txt %{buildroot}%{_licensedir}/unrar/license.txt

%files -f %{_sourcedir}/unrar.filelist

%changelog
* Sat Nov 21 2026 tenko <build@tenko.invalid> 7.2.7-1
- New package, not in the base set: latest upstream stable release
  (7.2.7, checked 2026-11-21).
