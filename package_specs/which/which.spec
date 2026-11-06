Name:       which
Version:    2.25
Release:    2
Summary:    Shows the full path of (shell) commands
License:    GPL-3.0-or-later
URL:        https://www.gnu.org/software/which/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
GNU which shows the full path of (shell) commands installed in your PATH.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir

%files -f %{_sourcedir}/which.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.25-2
- Rebuild and re-verify against the pinned version (which 2.25, md5
  60140cb2637634e4f4e68c2e98c6a07b); no version change needed

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.25
- Update to 2.25
- Replace the directory listing with a generated static filelist
