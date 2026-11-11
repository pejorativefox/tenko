Name:       wmname
Version:    0.1
Release:    1
Summary:    Prints or sets the window manager name
License:    MIT
URL:        https://tools.suckless.org/wmname/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: gcc, make
BuildRequires: libx11
BuildRequires: libXdmcp
BuildRequires: libxau
BuildRequires: libxcb
BuildRequires: xorgproto

%description
wmname prints or sets the window manager name property of the root
window, which is useful for working around Java and other toolkits
that misdetect the running window manager.

%prep
%setup -q

%build
%make_build

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} PREFIX=/usr

%files -f %{_sourcedir}/wmname.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.1-1
- Not in the base set; latest upstream stable 2026-11-05
  (0.1, 2012).  Built with the upstream plain Makefile against libX11.
