Name:       nettle
Version:    4.0
Release:    3
Summary:    A low-level cryptographic library
License:    GPL-2.0-or-later AND LGPL-3.0-or-later
URL:        https://www.lysator.liu.se/~nisse/nettle/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
BuildRequires: texinfo

%description
Nettle is a low-level cryptographic library that is designed to fit easily
in many contexts.  It provides the hash functions, ciphers, and public-key
primitives used by GnuTLS.

%package doc
Summary:    nettle documentation
Requires:   nettle = %{version}-%{release}

%description doc
Documentation for nettle.

%prep
%setup -q

%build
%configure --prefix=/usr --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -rf %{buildroot}%{_infodir}/dir

# installs the pre-built manual alongside the info file.
install -d %{buildroot}%{_docdir}/%{name}-%{version}
install -m644 nettle.html nettle.pdf \
        %{buildroot}%{_docdir}/%{name}-%{version}

%files -f %{_sourcedir}/nettle.filelist
%files doc -f %{_sourcedir}/nettle-doc.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.0-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.0-2
- Split doc, devel payload into nettle-doc, nettle-devel (size audit)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.0
- Update to 4.0
- Install manual copy under /usr/share/doc/nettle-4.0
- Replace the hand-written file list with a generated static filelist

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 3.4
- Initial RPM
