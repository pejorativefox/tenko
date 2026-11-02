Name:       cryptsetup
Version:    2.8.8
Release:    1
Summary:    Userspace setup tool for transparent block device encryption
License:    GPL-2.0-or-later
URL:        https://gitlab.com/cryptsetup/cryptsetup
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: json-c
BuildRequires: popt
BuildRequires: openssl-devel
BuildRequires: LVM2-devel
BuildRequires: util-linux-devel

%description
cryptsetup is used to set up transparent encryption of block devices using
the kernel crypto API. It provides the cryptsetup, veritysetup and
integritysetup utilities and the libcryptsetup library.

%package lang
Summary:    cryptsetup translations
Requires:   %{name} = %{version}-%{release}

%description lang
Translations for cryptsetup.

%package devel
Summary:    Development files for libcryptsetup
Requires:   %{name} = %{version}-%{release}

%description devel
Headers, pkg-config metadata and linker symlinks for libcryptsetup.

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
%files devel -f %{_sourcedir}/cryptsetup-devel.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.8.8-1
- New package at the BLFS r13.1 version (2.8.8).
- Built with the book's configure options: --disable-ssh-token and
  --disable-asciidoc; default OpenSSL crypto backend, json-c, popt and
  libdevmapper (LVM2) required.
