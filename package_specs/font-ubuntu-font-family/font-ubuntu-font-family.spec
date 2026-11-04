# The Ubuntu Font Family sources tarball from the Debian/Ubuntu packaging
# is the canonical distribution artifact: it carries the final User .ttf
# files and the README/LICENCE-FAQ.  No build step.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       font-ubuntu-font-family
Version:    0.83
Release:    1
Summary:    The Ubuntu UI font family (User/packaging .ttfs, 0.83)
License:    Ubuntu-UFL
Prefix:     /usr
Source0:    ubuntu-font-family-sources_0.83.orig.tar.gz

ExclusiveArch: x86_64

AutoProv: no
AutoReq: no

%description
The Ubuntu Font Family is a set of sans-serif OpenType fonts sponsored by
Canonical and produced by Dalton Maag.  Version 0.83 ships the packaged
user-facing artifacts: the named weights of Ubuntu (Light, Regular, Bold,
Italic…), plus the Ubuntu Mono family, together with the Ubuntu Font
Licence (UFL) text and README notes.

The Ubuntu Font Family is not in LFS/BLFS.  The user explicitly requested
packaging it as an exception to the Browneye version-parity rule; the
Debian/Ubuntu packaging source tarball is used verbatim.

Payload = every .ttf inside the tarball + README.txt and LICENCE.txt for
the license terms (Ubuntu Font Licence version 1.0).

%prep

%build

%install
rm -rf %{buildroot}
tmp=$(mktemp -d)
tar -xzf %{SOURCE0} -C $tmp
install -d -m 0755 %{buildroot}/usr/share/fonts/ubuntu-font-family
for t in $tmp/ubuntu-font-family-sources-0.83/*.ttf; do
    install -m 0644 "$t" %{buildroot}/usr/share/fonts/ubuntu-font-family/
done
install -m 0644 $tmp/ubuntu-font-family-sources-0.83/README.txt \
    %{buildroot}/usr/share/fonts/ubuntu-font-family/README.txt
install -m 0644 $tmp/ubuntu-font-family-sources-0.83/LICENCE.txt \
    %{buildroot}/usr/share/fonts/ubuntu-font-family/LICENCE.txt
rm -rf $tmp

%files -f %{_sourcedir}/font-ubuntu-font-family.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.83
- Repackage the canonical Ubuntu Font Family 0.83 packaging tarball
  (Ubuntu + Ubuntu Mono ttf files) exactly as upstream ships it, with
  README.txt and LICENCE.txt (Ubuntu-UFL)
- Static %files filelist, license text shipped in the payload
