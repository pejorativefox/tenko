Name:       perl
Version:    5.44.0
Release:    6
Summary:    Perl programming language
License:    Artistic-1.0-Perl OR GPL-1.0-or-later
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

%package doc
Summary:    Perl documentation
License:    Artistic-1.0-Perl OR GPL-1.0-or-later

%description doc
Perl man pages and the core Perl POD documentation.

%files -f %{_sourcedir}/perl.filelist
%files doc -f %{_sourcedir}/perl-doc.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 5.44.0-6
- Record the verified license (Artistic-1.0-Perl OR GPL-1.0-or-later): README (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 5.44.0-5
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 5.44.0-4
- Rebuild with a working perl on the build host.  The 5.44.0-3 build ran in
  an image whose perl could not start (no libperl.so), so rpm's perl.prov
  generator silently produced only 2 perl(...) provides instead of 891 and
  vim-minimal's perl(Getopt::Long) & co. became unsatisfiable.  No payload
  change from -3.
* Mon Nov 02 2026 browneye <build@browneye.invalid> 5.44.0-3
- Ship libperl.so in the runtime package.  /usr/bin/perl is linked against
  libperl.so (unversioned, the library has no SONAME) and finds it through
  RUNPATH=/usr/lib64/perl5/5.44.0/core_perl/CORE, but the -2 split put that
  file in perl-devel, so every perl invocation on a perl-only install died
  with "libperl.so: cannot open shared object file" (this host included).
  perl-devel keeps the CORE headers; the runtime now owns CORE/libperl.so.
* Sun Nov 01 2026 browneye <build@browneye.invalid> 5.44.0-2
- Split CORE development files and documentation into perl-devel and
  perl-doc (packaging only; versions unchanged)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 5.44.0
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 5.44.0
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 5.38.0-1
- Version bump
