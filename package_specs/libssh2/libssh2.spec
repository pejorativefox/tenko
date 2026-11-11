Name:       libssh2
Version:    1.11.1
Release:    2
Summary:    SSH2 protocol library
License:    BSD-3-Clause
URL:        https://libssh2.org/
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz
BuildRequires: openssl


%description
libssh2 is a library implementing the SSH2 protocol. It provides SSH
session, channel, SFTP and SCP functions for client applications.

%prep
%setup -a 0

%build
%configure --disable-static
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libssh2.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.11.1-2
- Replace the TODO summary/description and record the verified license
  (BSD-3-Clause): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.11.1-1
- Sync with the base set

# let's skip this for now

