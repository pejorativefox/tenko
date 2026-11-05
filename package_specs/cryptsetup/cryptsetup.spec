Name:       cryptsetup
Version:    2.8.8
Release:    2
Summary:    Userspace setup tool for transparent block device encryption
License:    GPL-2.0-or-later
URL:        https://gitlab.com/cryptsetup/cryptsetup
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: json-c
BuildRequires: popt
BuildRequires: openssl
BuildRequires: LVM2
BuildRequires: util-linux

%description
cryptsetup is used to set up transparent encryption of block devices using
the kernel crypto API. It provides the cryptsetup, veritysetup and
integritysetup utilities and the libcryptsetup library.

%package lang
Summary:    cryptsetup translations
Requires:   %{name} = %{version}-%{release}

%description lang
Translations for cryptsetup.

%prep
%setup -q

%build
%configure             \
    --disable-ssh-token \
    --disable-asciidoc
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/cryptsetup.filelist
%files lang -f %{_sourcedir}/cryptsetup-lang.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.8.8-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.8.8-1
- New package at the BLFS r13.1 version (2.8.8).
- Built with the book's configure options: --disable-ssh-token and
  --disable-asciidoc; default OpenSSL crypto backend, json-c, popt and
  libdevmapper (LVM2) required.
