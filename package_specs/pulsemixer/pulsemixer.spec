Name:       pulsemixer
Version:    1.5.1
Release:    2
Summary:    CLI and curses mixer for PulseAudio
License:    MIT
URL:        https://github.com/GeorgeFilipkin/pulsemixer
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

Requires:   python
Requires:   pulseaudio

%description
pulsemixer is a self-contained command line and curses mixer for
PulseAudio.  It needs only Python 3 and pactl, and provides the same
functionality as the GTK pavucontrol mixer in a terminal.

%prep
%setup -q

%build
# Single-file Python application: nothing to compile.

%install
rm -rf %{buildroot}
install -d -m755 %{buildroot}%{_bindir}
install -m755 pulsemixer %{buildroot}%{_bindir}/pulsemixer
install -d -m755 %{buildroot}%{_docdir}/pulsemixer-%{version}
install -m644 LICENSE README.md \
    %{buildroot}%{_docdir}/pulsemixer-%{version}/

%files
/usr/bin/pulsemixer
/usr/share/doc/pulsemixer-%{version}/LICENSE
/usr/share/doc/pulsemixer-%{version}/README.md

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.5.1-2
- Require the distro's `python` package (it provides /usr/bin/python3);
  there is no python3 capability in this tree.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.5.1-1
- New package: user-approved replacement for pavucontrol (not in
  the base set); single-file MIT Python 3 curses mixer, needs only pactl
