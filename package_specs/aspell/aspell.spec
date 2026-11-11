Name:       aspell
Version:    0.60.8.3
Release:    1
Summary:    Spell checker library and command line tool
License:    LGPL-2.1
URL:        http://aspell.net/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Aspell is a spell checker library and command line tool, with a
separate dictionary per language.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
ln -sfn aspell-0.60 %{buildroot}/usr/lib64/aspell
install -d -m755 %{buildroot}/usr/share/doc/aspell-%{version}/aspell{.html,-dev.html}
install -m644 manual/aspell.html/* \
        %{buildroot}/usr/share/doc/aspell-%{version}/aspell.html
install -m644 manual/aspell-dev.html/* \
        %{buildroot}/usr/share/doc/aspell-%{version}/aspell-dev.html
rm -f %{buildroot}/usr/lib64/*.la %{buildroot}/%{_infodir}/dir

%files -f %{_sourcedir}/aspell.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.60.8.3-1
- New package, required by enchant
