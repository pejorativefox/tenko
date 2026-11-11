Name:       sassc
Version:    3.6.2
Release:    1
Summary:    Command-line Sass compiler
License:    MIT
URL:        https://github.com/sass/sassc
Prefix:     /usr
Source0:    sassc-3.6.2.tar.gz
Source1:    libsass-3.6.6.tar.gz

%description
sassc is a command-line wrapper around libsass for compiling SCSS
stylesheets.  libsass is linked statically into the binary, so the
package has no runtime library dependency.

%prep
%setup -q -n sassc-%{version} -a 1

%build
make %{?_smp_mflags} BUILD=static \
     SASSC_VERSION=%{version} \
     SASS_LIBSASS_PATH=%{_builddir}/sassc-%{version}/libsass-3.6.6

%install
rm -rf %{buildroot}
install -Dpm755 bin/sassc %{buildroot}%{_bindir}/sassc
install -Dpm644 LICENSE %{buildroot}%{_licensedir}/sassc/LICENSE
install -Dpm644 libsass-3.6.6/LICENSE \
    %{buildroot}%{_licensedir}/sassc/LICENSE.libsass

%files -f %{_sourcedir}/sassc.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 3.6.2-1
- New package (sassc 3.6.2, latest stable upstream; libsass 3.6.6,
  latest stable upstream, linked statically) so arc-theme can be built
  without an Inkscape or Sass toolchain in the base image.
