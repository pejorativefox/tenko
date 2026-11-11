Name:       powertop
Version:    2.16.1
Release:    1
Summary:    Diagnose power consumption and power management issues
License:    GPL-2.0-only
URL:        https://github.com/fenrus75/powertop
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: meson
BuildRequires: ninja
BuildRequires: gcc
BuildRequires: ncurses
BuildRequires: libnl
BuildRequires: libtracefs
BuildRequires: pciutils
BuildRequires: gettext
BuildRequires: bash-completion

%description
PowerTOP is a Linux tool that diagnoses issues with power consumption and
power management.  Its interactive terminal interface reports per-process
wakeups, CPU idle and frequency states, device power states, and tunables
that can be changed at runtime.  It can also write HTML, CSV and Markdown
reports from a measurement run.

PowerTOP is not part of the base set; it is packaged as an optional
diagnostic tool.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup --prefix=/usr --buildtype=release -Dnls=true ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/powertop.filelist

%changelog
* Wed Nov 11 2026 browneye <build@browneye.invalid> 2.16.1-1
- New package: PowerTOP 2.16.1 (latest stable upstream).  It is not in
  the base set; it is an optional power diagnostic tool.
- Source: https://github.com/fenrus75/powertop/archive/refs/tags/v2.16.1.tar.gz
  md5 60b1441ee4fabfa8ef9dd68dca289944
  sha256 73d5e96d992ed7f040e17c6c9130deebcf42c38990711840981c7afac6f7832f
- Build against the packaged ncurses, libnl, libtracefs and pciutils;
  libtracefs is a new dependency added with this package.
- Installed files: the powertop binary and man page, the bash completion,
  and the native-language message catalogs.
