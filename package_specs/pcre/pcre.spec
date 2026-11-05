Name:       pcre
Version:    8.45
Release:    1
Summary:    Perl-compatible regular expression library (PCRE1)
License:    BSD-3-Clause
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2


%description
The PCRE library is a set of functions that implement regular
expression pattern matching using the same syntax and semantics as
Perl.  This is the PCRE1 (8.x) line.

%prep
%setup -q

%build
%configure  --docdir=/usr/share/doc/pcre-%{version} \
            --enable-unicode-properties       \
            --enable-pcre16                   \
            --enable-pcre32                   \
            --enable-pcregrep-libz            \
            --enable-pcregrep-libbz2          \
            --enable-pcretest-libreadline     \
            --disable-static
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/pcre.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 8.45-1
- Update 8.42 -> 8.45, the final PCRE1 release.
- Basis: the PCRE1 line is archive-only in the r13.1 book;
  8.45 is its final upstream release.  This spec stays on PCRE1;
  pcre2 is a separate package.
- Source: https://sourceforge.net/projects/pcre/files/pcre/8.45/pcre-8.45.tar.bz2
  md5 4452288e6a0eefb2ab11d36010a1eebb
- --docdir updated to pcre-8.45; same build options as before.
- Static filelist generated from the install tree.
