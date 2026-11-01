Name:       nettle
Version:    4.0
Release:    1
Summary:    A low-level cryptographic library
License:    GPL-2.0-or-later AND LGPL-3.0-or-later
URL:        https://www.lysator.liu.se/~nisse/nettle/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Nettle is a low-level cryptographic library that is designed to fit easily
in many contexts.  It provides the hash functions, ciphers, and public-key
primitives used by GnuTLS.

%prep
%setup -q

%build
%configure --prefix=/usr --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -rf %{buildroot}%{_infodir}/dir

# BLFS installs the pre-built manual alongside the info file.
install -d %{buildroot}%{_docdir}/%{name}-%{version}
install -m644 nettle.html nettle.pdf \
        %{buildroot}%{_docdir}/%{name}-%{version}

%files -f %{_sourcedir}/nettle.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.0
- Update to 4.0 (BLFS r13.1)
- Install the BLFS manual copy under /usr/share/doc/nettle-4.0
- Replace the hand-written file list with a generated static filelist

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 3.4
- Initial RPM
