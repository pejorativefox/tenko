Name:       jq
Version:    1.8.2
Release:    1
Summary:    Command-line JSON processor
License:    MIT AND ICU AND BSD-2-Clause AND CC-BY-3.0
URL:        https://jqlang.org/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: gcc
BuildRequires: make

%description
jq is a lightweight and flexible command-line JSON processor.  It works like
sed for JSON data: it slices, filters, maps and transforms structured data,
and can be used both interactively and in scripts.

%prep
%setup -q

%build
%configure --with-oniguruma=builtin --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
# The bundled Oniguruma provides jq's regex engine.  Ship its runtime
# library, not the development files of a private vendored copy.
rm -f %{buildroot}%{_bindir}/onig-config
rm -f %{buildroot}%{_includedir}/oniguruma.h
rm -f %{buildroot}%{_includedir}/oniggnu.h
rm -f %{buildroot}%{_includedir}/onigposix.h
rm -f %{buildroot}%{_libdir}/pkgconfig/oniguruma.pc
rm -f %{buildroot}%{_libdir}/libonig.so
rm -f %{buildroot}%{_libdir}/*.la

%files -f %{_sourcedir}/jq.filelist

%changelog
* Thu Nov 12 2026 tenko <build@tenko.invalid> 1.8.2-1
- New package, not in the base set: latest upstream stable release
  (1.8.2, checked 2026-11-12).
