Name:       bdftopcf
Version:    1.1.1
Release:    1
Summary:    bdftopcf font conversion
License:    GPL
Source0:    bdftopcf-1.1.1.tar.xz
Prefix:     /usr

%description
bdftopcf font conversion

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/bdftopcf.filelist
%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.1.1
- Sync with BLFS r13.1 (bdftopcf 1.1.1)
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.1.1
- Sync with BLFS r13.1 (bdftopcf 1.1.1)
* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.1
- Initial RPM

