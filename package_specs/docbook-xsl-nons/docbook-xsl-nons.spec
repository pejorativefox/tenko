Name:       docbook-xsl-nons
Version:    1.79.2
Release:    3
Summary:    XSL stylesheets for transforming DocBook XML
License:    MIT AND BSD-3-Clause AND Apache-2.0
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2
Patch0:     docbook-xsl-nons-1.79.2-stack_fix-1.patch
Requires:   libxml2

%description
These are XSL stylesheets for transforming DocBook XML document instances
into various output formats. This package contains the non-namespaced
stylesheets.

%prep
%setup -a 0
%patch -P 0 -p1

%build


%install    
rm -rf %{buildroot}

install -v -m755 -d %{buildroot}/usr/share/xml/docbook/xsl-stylesheets-nons-1.79.2

cp -v -R VERSION assembly common eclipse epub epub3 extensions fo        \
         highlighting html htmlhelp images javahelp lib manpages params  \
         profiling roundtrip slides template tests tools webhelp website \
         xhtml xhtml-1_1 xhtml5                                          \
    %{buildroot}/usr/share/xml/docbook/xsl-stylesheets-nons-1.79.2

ln -s VERSION %{buildroot}/usr/share/xml/docbook/xsl-stylesheets-nons-1.79.2/VERSION.xsl

install -v -m644 -D README \
                    %{buildroot}/usr/share/doc/docbook-xsl-nons-1.79.2/README.txt
install -v -m644    RELEASE-NOTES* NEWS* \
                    %{buildroot}/usr/share/doc/docbook-xsl-nons-1.79.2



%post
mkdir -p /etc/xml
if [ ! -e /etc/xml/catalog ]; then
    xmlcatalog --noout --create /etc/xml/catalog
fi
for uri in http://cdn.docbook.org/release/xsl-nons/1.79.2 \
           https://cdn.docbook.org/release/xsl-nons/1.79.2 \
           http://cdn.docbook.org/release/xsl-nons/current \
           https://cdn.docbook.org/release/xsl-nons/current \
           http://docbook.sourceforge.net/release/xsl/current; do
    for rewrite in System URI; do
        xmlcatalog --noout --add "rewrite$rewrite" "$uri" \
            "/usr/share/xml/docbook/xsl-stylesheets-nons-1.79.2" /etc/xml/catalog
    done
done

%postun
if [ "$1" -eq 0 ]; then
    for uri in http://cdn.docbook.org/release/xsl-nons/1.79.2 \
               https://cdn.docbook.org/release/xsl-nons/1.79.2 \
               http://cdn.docbook.org/release/xsl-nons/current \
               https://cdn.docbook.org/release/xsl-nons/current \
               http://docbook.sourceforge.net/release/xsl/current; do
        for rewrite in System URI; do
            xmlcatalog --noout --del "rewrite$rewrite" "$uri" /etc/xml/catalog || :
        done
    done
fi

%files -f %{_sourcedir}/docbook-xsl-nons.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.79.2-3
- Replace the TODO summary/description and record the verified license
  (MIT AND BSD-3-Clause AND Apache-2.0): COPYING, extensions/LICENSE.txt (issue #8).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.79.2-2
- Install the XML catalog rewrites (cdn.docbook.org and
  docbook.sourceforge.net) that the package page wires up, so xsltproc --nonet
  can find docbook.xsl.  This is what xfce4-terminal's man page needs (D8).
# let's skip this for now

