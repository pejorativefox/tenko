Name:       tar
Version:    1.35
Release:    3
Summary:    GNU tar utility
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The Tar package provides the ability to create tar archives as well as perform various other kinds of archive manipulation. Tar can be used on previously created archives to extract files, to store additional files, or to update or list files which were already stored. 

%package lang
Summary:    tar translations
Requires:   tar = %{version}-%{release}

%description lang
Translations for tar.

%prep
%setup -q
patch -Np1 -i %{_sourcedir}/tar-1.35-acl_fix-1.patch

%build
export FORCE_UNSAFE_CONFIGURE=1
%configure --without-selinux 
%make_build
unset FORCE_UNSAFE_CONFIGURE
%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/tar.filelist
%files lang -f %{_sourcedir}/tar-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.35-3
- Record the verified license (GPL-3.0-or-later): src/tar.c (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.35-2
- Split lang payload into tar-lang (size audit)

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 1.35-1
- Version bump
