Name:       groff
Version:    1.24.2
Release:    2
Summary:    GNU typesetting system
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
Recommends: groff-perl = %{version}-%{release}

%description
groff (GNU roff) is a typesetting system that reads plain text input files that include formatting commands to produce output in PostScript, PDF, HTML, or DVI formats or for display to a terminal. 

%prep
%setup -q

%build
export PAGE=letter
%configure
%make_build MOMPROCESSEDEXAMPLEFILES= PROCESSEDDOCFILES_PDF= \
    nodist_docpdfdoc_DATA= nodist_momprocessedexample_DATA= \
    nodist_sboxespdfdoc_DATA=
unset PAGE

%install
rm -rf %{buildroot}
%make_install MOMPROCESSEDEXAMPLEFILES= PROCESSEDDOCFILES_PDF= \
    nodist_docpdfdoc_DATA= nodist_momprocessedexample_DATA= \
    nodist_sboxespdfdoc_DATA= PDFDOCFILE=
rm -vf %{buildroot}%{_infodir}/dir*

%package perl
Summary:    groff Perl helper scripts
License:    GPL-3.0-or-later
Requires:   groff = %{version}-%{release}
Requires:   perl

%description perl
The groff helpers that are written in Perl: chem, gperl, glilypond,
gpinyin, afmtodit, grog, gropdf, mmroff and pdfmom.  The groff package
recommends this one; installing groff without it leaves the core roff
formatters (troff, nroff, groff, eqn, tbl, pic, refer) and man-page
rendering fully functional, but these optional front ends are absent.

%package doc
Summary:    groff documentation and examples
License:    GFDL-1.3-or-later OR GPL-3.0-or-later

%description doc
The groff HTML manual, info files and example documents.

%files -f %{_sourcedir}/groff.filelist
%files perl -f %{_sourcedir}/groff-perl.filelist
%files doc -f %{_sourcedir}/groff-doc.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.24.2-2
- Record the verified license (GPL-3.0-or-later): LICENSES, FDL and doc/groff.texi (issue #8).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 1.24.2-1
- Update to 1.24.2 (current upstream version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.24.1-2
- Split the Perl helper scripts and documentation out of groff; perl is no
  longer a hard runtime requirement (packaging only; versions unchanged)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.24.1
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump
