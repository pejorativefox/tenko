Name:       docbook-xml
Version:    4.5
Release:    1
Summary:    DocBook XML 4.5 DTD and catalog
License:    MIT
URL:        https://docbook.org/
BuildArch:  noarch
Prefix:     /usr
Source0:    docbook-xml-4.5.zip
Requires:   libxml2

%description
The DocBook XML 4.5 Document Type Definition, its modules and its catalog.
It lets tooling resolve the canonical OASIS DocBook 4.5 URLs locally, which
is what xfce4-terminal (and other packages) need to build their man pages
with xsltproc --nonet.

%prep
rm -rf %{name}-%{version}
mkdir %{name}-%{version}
cd %{name}-%{version}
python3 -m zipfile -e %{SOURCE0} .

%install
rm -rf %{buildroot}
cd %{name}-%{version}
install -d -m755 %{buildroot}/etc/xml
install -d -m755 %{buildroot}/usr/share/xml/docbook/xml-dtd-%{version}
cp -af catalog.xml docbook.cat *.dtd ent *.mod \
    %{buildroot}/usr/share/xml/docbook/xml-dtd-%{version}/
# Resolve the DTD's canonical URLs to the local copy.
xmlcatalog --noout --add "rewriteSystem" \
    "http://www.oasis-open.org/docbook/xml/%{version}" \
    "file:///usr/share/xml/docbook/xml-dtd-%{version}" \
    %{buildroot}/usr/share/xml/docbook/xml-dtd-%{version}/catalog.xml
xmlcatalog --noout --add "rewriteURI" \
    "http://www.oasis-open.org/docbook/xml/%{version}" \
    "file:///usr/share/xml/docbook/xml-dtd-%{version}" \
    %{buildroot}/usr/share/xml/docbook/xml-dtd-%{version}/catalog.xml

%post
mkdir -p /etc/xml
if [ ! -e /etc/xml/catalog ]; then
    xmlcatalog --noout --create /etc/xml/catalog
fi
CAT=file:///usr/share/xml/docbook/xml-dtd-%{version}/catalog.xml
for pub in "-//OASIS//ENTITIES DocBook XML" "-//OASIS//DTD DocBook XML"; do
    xmlcatalog --noout --add "delegatePublic" "$pub" "$CAT" /etc/xml/catalog
done
xmlcatalog --noout --add "delegateSystem" "http://www.oasis-open.org/docbook/" "$CAT" /etc/xml/catalog
xmlcatalog --noout --add "delegateURI" "http://www.oasis-open.org/docbook/" "$CAT" /etc/xml/catalog

%postun
if [ "$1" -eq 0 ]; then
    CAT=file:///usr/share/xml/docbook/xml-dtd-%{version}/catalog.xml
    for pub in "-//OASIS//ENTITIES DocBook XML" "-//OASIS//DTD DocBook XML"; do
        xmlcatalog --noout --del "delegatePublic" "$pub" "$CAT" /etc/xml/catalog || :
    done
    xmlcatalog --noout --del "delegateSystem" "http://www.oasis-open.org/docbook/" "$CAT" /etc/xml/catalog || :
    xmlcatalog --noout --del "delegateURI" "http://www.oasis-open.org/docbook/" "$CAT" /etc/xml/catalog || :
fi

%files -f %{_sourcedir}/docbook-xml.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.5-1
- New package (D8): DocBook XML 4.5 DTD, its modules and the XML catalog
  wiring, so xsltproc can resolve the OASIS DocBook URLs offline.  This is
  what the xfce4-terminal man page build needs.
