Name:       tmux
Version:    3.8
Release:    1
Summary:    tmux terminal multiplexer
License:    ISC
URL:        https://github.com/tmux/tmux
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: libevent
BuildRequires: ncurses

%description
tmux is a terminal multiplexer. It lets you switch easily between several programs in one terminal, detach them (they keep running in the background) and reattach them to a different terminal.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/tmux.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.8-1
- Not in the base set: bump to the latest upstream
  stable release (3.8, checked 2026-11-05).

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 3.3a
- Initial RPM
