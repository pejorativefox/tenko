Name:       rxvt-unicode
Version:    9.31
Release:    2
Summary:    rxvt-unicode is a fork of the well known terminal emulator rxvt.
License:    GPL-3.0-or-later AND (BSD-2-Clause OR GPL-2.0-or-later)
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
rxvt-unicode is a fork of the well known terminal emulator rxvt.

%prep
%setup

%build
sed '/interpolation/,+7d' -i src/rxvtutil.h
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/bin/urclock
/usr/bin/urxvt
/usr/bin/urxvtc
/usr/bin/urxvtd
/usr/lib64/urxvt/perl/background
/usr/lib64/urxvt/perl/bell-command
/usr/lib64/urxvt/perl/block-graphics-to-ascii
/usr/lib64/urxvt/perl/clickthrough
/usr/lib64/urxvt/perl/clipboard-osc
/usr/lib64/urxvt/perl/confirm-paste
/usr/lib64/urxvt/perl/digital-clock
/usr/lib64/urxvt/perl/eval
/usr/lib64/urxvt/perl/example-refresh-hooks
/usr/lib64/urxvt/perl/keysym-list
/usr/lib64/urxvt/perl/kuake
/usr/lib64/urxvt/perl/matcher
/usr/lib64/urxvt/perl/option-popup
/usr/lib64/urxvt/perl/overlay-osc
/usr/lib64/urxvt/perl/readline
/usr/lib64/urxvt/perl/remote-clipboard
/usr/lib64/urxvt/perl/searchable-scrollback
/usr/lib64/urxvt/perl/selection
/usr/lib64/urxvt/perl/selection-autotransform
/usr/lib64/urxvt/perl/selection-pastebin
/usr/lib64/urxvt/perl/selection-popup
/usr/lib64/urxvt/perl/selection-to-clipboard
/usr/lib64/urxvt/perl/tabbed
/usr/lib64/urxvt/perl/urxvt-popup
/usr/lib64/urxvt/perl/xim-onthespot
/usr/lib64/urxvt/urxvt.pm
/usr/share/man/man1/urclock.1.gz
/usr/share/man/man1/urxvt-background.1.gz
/usr/share/man/man1/urxvt-bell-command.1.gz
/usr/share/man/man1/urxvt-block-graphics-to-ascii.1.gz
/usr/share/man/man1/urxvt-clickthrough.1.gz
/usr/share/man/man1/urxvt-clipboard-osc.1.gz
/usr/share/man/man1/urxvt-confirm-paste.1.gz
/usr/share/man/man1/urxvt-digital-clock.1.gz
/usr/share/man/man1/urxvt-eval.1.gz
/usr/share/man/man1/urxvt-example-refresh-hooks.1.gz
/usr/share/man/man1/urxvt-extensions.1.gz
/usr/share/man/man1/urxvt-keysym-list.1.gz
/usr/share/man/man1/urxvt-kuake.1.gz
/usr/share/man/man1/urxvt-matcher.1.gz
/usr/share/man/man1/urxvt-option-popup.1.gz
/usr/share/man/man1/urxvt-overlay-osc.1.gz
/usr/share/man/man1/urxvt-readline.1.gz
/usr/share/man/man1/urxvt-remote-clipboard.1.gz
/usr/share/man/man1/urxvt-searchable-scrollback.1.gz
/usr/share/man/man1/urxvt-selection-autotransform.1.gz
/usr/share/man/man1/urxvt-selection-pastebin.1.gz
/usr/share/man/man1/urxvt-selection-popup.1.gz
/usr/share/man/man1/urxvt-selection-to-clipboard.1.gz
/usr/share/man/man1/urxvt-selection.1.gz
/usr/share/man/man1/urxvt-tabbed.1.gz
/usr/share/man/man1/urxvt-xim-onthespot.1.gz
/usr/share/man/man1/urxvt.1.gz
/usr/share/man/man1/urxvtc.1.gz
/usr/share/man/man1/urxvtd.1.gz
/usr/share/man/man3/urxvtperl.3.gz
/usr/share/man/man7/urxvt.7.gz

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 9.31-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-3.0-or-later AND (BSD-2-Clause OR GPL-2.0-or-later)): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 9.31-1
- Sync with BLFS r13.1

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 9.22-1
- Initial RPM

