Name:       libpwquality
Version:    1.4.5
Release:    1
Summary:    Password quality checking and random password generation library
License:    BSD-3-Clause OR GPL-2.0-or-later
URL:        https://github.com/libpwquality/libpwquality
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: cracklib
BuildRequires: gettext
BuildRequires: linux-pam

# pwquality opens the CrackLib dictionary at run time.
Requires:   cracklib

%description
libpwquality checks the quality of a password against configurable rules
and the CrackLib dictionary, and generates random passwords.  The package
ships the library, the pwscore and pwmake tools, /etc/security/pwquality.conf
and the pam_pwquality module.  No PAM stack uses the module by default.

%prep
%setup -q

%build
%configure \
    --disable-static \
    --disable-python-bindings \
    --enable-pam \
    --with-securedir=/usr/lib64/security
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libpwquality.filelist

%changelog
* Mon Nov 16 2026 tenko <build@tenko.invalid> 1.4.5-1
- New package, not in the base set: latest upstream stable release
  (1.4.5, checked 2026-11-16).  Required by Seahorse.
- Built without the Python binding.  pam_pwquality is installed in
  /usr/lib64/security but no PAM service file references it.
