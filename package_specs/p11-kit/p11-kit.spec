Name:       p11-kit
Version:    0.26.5
Release:    1
Summary:    Load and enumerate PKCS#11 modules
License:    BSD-3-Clause
URL:        https://p11-glue.github.io/p11-glue/p11-kit.html
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: libtasn1
BuildRequires: meson
BuildRequires: ninja
Requires:      libtasn1

%description
p11-kit provides a way to load and enumerate PKCS#11 modules.  Its trust
module exposes the system certificate anchors to PKCS#11 consumers, and
the trust utility extracts OpenSSL/GnuTLS certificate stores from those
anchors.

%prep
%setup -q

sed '20,$ d' -i trust/trust-extract-compat
cat >> trust/trust-extract-compat << "END"
# Copy existing anchor modifications to /etc/ssl/local
/usr/libexec/make-ca/copy-trust-modifications

# Update trust stores
/usr/sbin/make-ca -r
END

%build
mkdir p11-build
cd p11-build
meson setup ..                 \
      --prefix=/usr            \
      --buildtype=release      \
      -D trust_paths=/etc/pki/anchors
ninja -j8

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C p11-build install
mkdir -p %{buildroot}%{_bindir}
ln -sf /usr/libexec/p11-kit/trust-extract-compat \
       %{buildroot}%{_bindir}/update-ca-certificates

%files -f %{_sourcedir}/p11-kit.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.26.5
- Update to 0.26.5 (BLFS r13.1)
- Switch from autotools to meson with trust_paths=/etc/pki/anchors
- Replace the directory listing with a generated static filelist
