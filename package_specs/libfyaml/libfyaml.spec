Name:       libfyaml
Version:    0.9.6
Release:    1
Summary:    Fully feature complete YAML parser and emitter
License:    MIT
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
libfyaml is a YAML 1.2 parser and emitter library.  AppStream requires it to
read its YAML metadata catalogues.

%prep
%setup -q

%build
%configure --disable-static --without-libclang
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libfyaml.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.9.6-1
- New package, synced with BLFS r13.1.  Required by AppStream.
