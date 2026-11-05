Name:       texinfo
Version:    7.3
Release:    3
Summary:    GNU texinfo utility
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

AutoReq: no

Requires: libc.so.6()(64bit), libncursesw.so.6()(64bit), perl >= 0:5.004

%description
The Texinfo package contains programs for reading, writing, and converting info pages. 

%package lang
Summary:    texinfo translations
Requires:   texinfo = %{version}-%{release}

%description lang
Translations for texinfo.

%package doc
Summary:    texinfo documentation
Requires:   texinfo = %{version}-%{release}

%description doc
Documentation for texinfo.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/texinfo.filelist
%files lang -f %{_sourcedir}/texinfo-lang.filelist
%files doc -f %{_sourcedir}/texinfo-doc.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 7.3-3
- Record the verified license (GPL-3.0-or-later): install-info/install-info.c (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 7.3-2
- Split lang, doc payload into texinfo-lang, texinfo-doc (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 7.3
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 7.0.3-1
- Version bump
