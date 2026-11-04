Name:       itstool
Version:    2.0.7
Release:    1
Summary:    Translate XML documents with PO files
License:    GPL3
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
* Wed Nov 04 2026 browneye <build@browneye.invalid> 2.0.7-1
- New package, synced with BLFS r13.1, including the BLFS lxml patch
  (itstool-2.0.7-lxml-1.patch).  Required by AppStream.
