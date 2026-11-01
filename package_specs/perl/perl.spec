Name:       perl
Version:    5.44.0
Release:    2
Summary:    Perl programming language
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

AutoReq: no

Provides: /bin/perl
Provides: perl = %{version}-%{release}
Provides: perl >= 1:5.6
Provides: libperl.so
Provides: perl(File::HomeDir)

Requires: libc.so.6()(64bit), libcrypt.so.2()(64bit), libdl.so.2()(64bit), libgdbm.so.6()(64bit), libgdbm_compat.so.4()(64bit)
Requires: libm.so.6()(64bit), libpthread.so.0()(64bit), librt.so.1()(64bit), libutil.so.1()(64bit)


%description
Perl programming language

%prep
%setup -q

%build
export BUILD_ZLIB=False
export BUILD_BZIP2=0
sh Configure -des                                         \
             -Dprefix=/usr                                \
             -Dvendorprefix=/usr                          \
             -Dprivlib=%{_libdir}/perl5/%{version}/core_perl      \
             -Darchlib=%{_libdir}/perl5/%{version}/core_perl      \
             -Dsitelib=%{_libdir}/perl5/%{version}/site_perl      \
             -Dsitearch=%{_libdir}/perl5/%{version}/site_perl     \
             -Dvendorlib=%{_libdir}/perl5/%{version}/vendor_perl  \
             -Dvendorarch=%{_libdir}/perl5/%{version}/vendor_perl \
             -Dman1dir=/usr/share/man/man1                \
             -Dman3dir=/usr/share/man/man3                \
             -Dpager="/usr/bin/less -isR"                 \
             -Duseshrplib                                 \
             -Dusethreads 
unset BUILD_ZLIB BUILD_BZIP2
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
rm -f %{buildroot}/usr/share/man/man3/Thread.3

%package devel
Summary:    Perl development files (CORE headers and linker files)
License:    GPL3
Requires:   perl = %{version}-%{release}

%description devel
The Perl CORE headers, configuration headers and libperl.so linker stub
needed to build and embed XS extensions.  ExtUtils::MakeMaker and the rest
of the module toolchain remain in the perl runtime package.

%package doc
Summary:    Perl documentation
License:    GPL3

%description doc
Perl man pages and the core Perl POD documentation.

%files -f %{_sourcedir}/perl.filelist
%files devel -f %{_sourcedir}/perl-devel.filelist
%files doc -f %{_sourcedir}/perl-doc.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 5.44.0-2
- Split CORE development files and documentation into perl-devel and
  perl-doc (packaging only; versions unchanged)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 5.44.0
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 5.44.0
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 5.38.0-1
- Version bump
