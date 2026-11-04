# xdg-utils 1.2.1 from BLFS r13.1 (xsoft/other/xdg-utils.xml).
#
# BLFS builds the man pages and the help text embedded in the shell scripts
# with xmlto + a text browser.  The base build image does not have that
# documentation toolchain, so the generated .txt help snippets and man pages
# are shipped as Source1, generated once from the same 1.2.1 source with
# xmlto 0.0.28, docbook-style-xsl and lynx.  The spec still builds the scripts
# from the upstream source; it only skips regenerating the docs.
Name:       xdg-utils
Version:    1.2.1
Release:    1
Summary:    Desktop integration command line tools
License:    MIT
URL:        https://www.freedesktop.org/wiki/Software/xdg-utils/
Prefix:     /usr
Source0:    xdg-utils-v%{version}.tar.gz
Source1:    xdg-utils-%{version}-generated.tar.gz

ExclusiveArch: x86_64

Requires:   coreutils
Requires:   desktop-file-utils
Requires:   shared-mime-info
Requires:   which
Requires:   xprop
Requires:   xset

%description
xdg-utils is a set of command line tools that assist applications with a
variety of desktop integration tasks, including opening URLs, managing
desktop entries and icons, querying MIME types, and setting the default
browser and mail client.  It is required for LSB conformance.

The man pages and the help text embedded in the scripts are generated from
the upstream DocBook sources; this package ships those generated files as a
side source because the browneye build image does not include xmlto.

%prep
%setup -q -n xdg-utils-v%{version}
tar -xzf %{SOURCE1}
# Make the pre-generated .txt files newer than the .in files so make uses
# them instead of trying to invoke xmlto.
touch scripts/*.txt scripts/man/*.1

%build
./configure --prefix=/usr
make -C scripts scripts

%install
rm -rf %{buildroot}
make -C scripts install DESTDIR=%{buildroot}

%files -f %{_sourcedir}/xdg-utils.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.2.1-1
- Initial package from BLFS r13.1 (xdg-utils 1.2.1)
- Build the shell scripts from source; ship the DocBook-generated help text
  and man pages as a side source because xmlto is not in the build image
