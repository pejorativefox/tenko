Name:       iw
Version:    6.17
Release:    1
Summary:    nl80211-based wireless configuration tool
License:    ISC
URL:        https://wireless.docs.kernel.org/en/latest/en/users/documentation/iw.html
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
BuildRequires: libnl
BuildRequires: linux-api-headers
BuildRequires: pkgconf

%description
iw is a nl80211-based command-line tool for configuring Linux wireless
devices.  It replaces the deprecated Wireless Extensions tools for modern
drivers and is used by TuneD's net plugin to read and set wireless power
saving.

%prep
%setup -q

%build
%make_build

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} PREFIX=/usr SBINDIR=/usr/sbin \
    MANDIR=/usr/share/man

%files -f %{_sourcedir}/iw.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 6.17-1
- New package: iw 6.17 (latest stable upstream).  Not in the base set;
  TuneD requires it and uses it to control wireless power saving.
