Name:       shared-mime-info
Version:    2.5.1
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz
%description
TODO

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                  \
      --prefix=/usr             \
      --buildtype=release       \
      -D update-mimedb=true     \
      -D build-tests=false      \
      -D build-spec=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/shared-mime-info.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.5.1
- Sync with BLFS r13.1 (1.10)

# let's skip this for now

