Name:       nmtui
Version:    1.58.1
Release:    1
Summary:    NetworkManager text user interface
License:    MIT
Prefix:     /usr
BuildArch:  noarch

# nmtui is built by NetworkManager itself (-D nmtui=true) and currently
# ships in the NetworkManager package.  This package gives it the name
# users expect from `dnf install nmtui`.
Requires:   NetworkManager >= %{version}
Provides:   NetworkManager-tui = %{version}-%{release}

%description
nmtui is the NetworkManager text user interface: nmtui, nmtui-connect,
nmtui-edit and nmtui-hostname.

The programs are installed by the NetworkManager package.  This package
exists so they can be installed by name; it only requires NetworkManager.

%prep

%build

%install
rm -rf %{buildroot}
install -d %{buildroot}/usr/share/tenko
cat > %{buildroot}/usr/share/tenko/nmtui <<'EOF'
nmtui is provided by the NetworkManager package.
EOF

%files -f %{_sourcedir}/nmtui.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 1.58.1-1
- New convenience package for the nmtui programs.  NetworkManager is
  already built with -D nmtui=true and ships /usr/bin/nmtui, so this
  package only requires it by name.
