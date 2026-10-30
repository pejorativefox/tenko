Name:       groff
Version:    1.24.1
Release:    1
Summary:    GNU typesetting system
License:    GPL3
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

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

%files -f %{_sourcedir}/groff.filelist

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.24.1
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump
