Name:       ncdu
Version:    1.22
Release:    1
Summary:    NCurses disk usage analyzer
License:    MIT
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: ncurses

%description
Ncdu is a disk usage analyzer with an ncurses interface. It is
designed to find space hogs on a remote server where you do not have a
full graphical setup available.

%prep
%setup -q -n %{name}-%{version}

%build
%configure --with-ncursesw
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/ncdu.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.22-1
- Not in the base set. The newest upstream stable (2.9.2) is a Zig
  rewrite and Zig is not in the distro, so the user approved the latest
  C-series release, 1.22 (2026-11-05).
- Build against the published ncurses 6.6; no -devel split and no
  static libraries.
