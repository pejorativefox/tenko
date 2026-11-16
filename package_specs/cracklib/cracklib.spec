Name:       cracklib
Version:    2.10.4
Release:    1
Summary:    Password strength checking library and dictionary
License:    LGPL-2.1-or-later
URL:        https://github.com/cracklib/cracklib
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: gettext
BuildRequires: zlib

%description
CrackLib tests a password against a dictionary of words and a set of rules
for weak passwords.  libpwquality uses it for its dictionary check.

The package ships the library, the dictionary tools and a packed dictionary
built from the word list in the source tarball (cracklib-small).

%prep
%setup -q

%build
%configure \
    --disable-static \
    --without-python \
    --with-default-dict=/usr/lib/cracklib/pw_dict
%make_build

%install
rm -rf %{buildroot}
%make_install

# The packed dictionary the library opens by default.  The tools are run
# from the build tree against the freshly built library.
install -dm755 %{buildroot}/usr/lib/cracklib
sh util/cracklib-format dicts/cracklib-small |
    ./util/cracklib-packer %{buildroot}/usr/lib/cracklib/pw_dict
for ext in hwm pwd pwi; do
    test -s %{buildroot}/usr/lib/cracklib/pw_dict.$ext
done

%files -f %{_sourcedir}/cracklib.filelist

%changelog
* Mon Nov 16 2026 tenko <build@tenko.invalid> 2.10.4-1
- New package, not in the base set: latest upstream stable release
  (2.10.4, checked 2026-11-16).  Required by libpwquality, which Seahorse
  needs.
- Built without the Python binding.  The default dictionary
  /usr/lib/cracklib/pw_dict is packed from the cracklib-small word list in
  the source tarball.
