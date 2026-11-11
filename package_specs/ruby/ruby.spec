Name:       ruby
Version:    4.0.9
Release:    1
Summary:    Ruby programming language
License:    BSDL
URL:        https://www.ruby-lang.org/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Ruby programming language

%prep
%setup

%build
%configure --disable-rpath       \
           --enable-shared       \
           --without-valgrind    \
           --without-baseruby    \
           ac_cv_func_qsort_r=no \
           --docdir=/usr/share/doc/ruby-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/ruby.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 4.0.9-1
- Sync with the base set

* Fri Sep 04 2020 Chris Statzer <chris.statzer@qq.com> 2.7.1
- Initial RPM

