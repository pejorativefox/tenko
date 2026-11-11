Name:       itstool
Version:    2.0.7
Release:    2
Summary:    Translate XML documents with PO files
License:    GPL-3.0-or-later
URL:        https://itstool.org/
Source0:    %{name}-%{version}.tar.gz
Patch0:     %{name}-%{version}-lxml-1.patch
BuildArch:  noarch
Requires:   python3-lxml
Requires:   docbook-xml
Prefix:     /usr

%description
itstool extracts translatable messages from XML documents and merges
translations back in.  AppStream uses it to localise its metainfo files.

%prep
%setup -q
%patch -P 0 -p1

%build
PYTHON=/usr/bin/python3 ./autogen.sh --prefix=/usr
make

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

%files -f %{_sourcedir}/itstool.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.0.7-2
- Record the verified license (GPL-3.0-or-later): COPYING (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 2.0.7-1
- New package, synced with the base set, including lxml patch
  (itstool-2.0.7-lxml-1.patch).  Required by AppStream.
