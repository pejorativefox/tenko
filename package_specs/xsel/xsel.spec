Name:       xsel
Version:    1.2.1
Release:    1
Summary:    Command-line program to get and set the X selection
License:    MIT
URL:        https://github.com/kfish/xsel
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: gcc, make, autoconf, automake, libtool, pkgconf
BuildRequires: libx11

%description
xsel is a command-line program for getting and setting the contents of the X
selection.  It operates on the PRIMARY selection by default and can also use
SECONDARY and CLIPBOARD, reading from standard input or writing to standard
output.

xsel 1.2.1 is the latest stable upstream release.

%prep
%setup -q

%build
# The GitHub release archive ships configure.ac but not the generated
# configure script.
autoreconf -vfi
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/xsel.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 1.2.1-1
- Initial package: xsel 1.2.1 (latest stable upstream release, GitHub tag
  1.2.1).  Not in the base set; user-requested clipboard utility.
- Build from the GitHub archive with autoreconf because the release archive
  does not include the generated configure script.
- Verified license MIT (COPYING).
