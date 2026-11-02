Name:       nmap
Version:    7.991
Release:    1
Summary:    Network exploration tool and security scanner
License:    NPSL
URL:        https://nmap.org/
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Nmap is a utility for network exploration and security auditing.  It supports
ping scanning, port scanning and TCP/IP fingerprinting.  The NSE scripting
engine and the bundled data files are included.

%package -n ncat
Summary:    Network utility for reading and writing data across networks
License:    NPSL

%description -n ncat
Ncat is a feature-packed networking utility which reads and writes data across
networks from the command line.  It is the Nmap Project's implementation of
netcat and is built from the nmap source tree.

%package -n nping
Summary:    Network packet generation and response analysis tool
License:    NPSL

%description -n nping
Nping is an open-source tool for network packet generation, response analysis
and response-time measurement.  It is built from the nmap source tree.

%prep
%setup -q

%build
# zenmap and ndiff need Python packaging tools (pypa-build and friends), which
# are not packaged.  They are not needed for nmap, ncat or nping.
#
# Use Nmap's bundled copies of PCRE2, Lua, libssh2 and liblinear: they are
# static internals and are not shipped as separate packages, and their bundled
# versions are at or above the BLFS r13.1 versions.  libpcap is the exception:
# the bundled 1.10.6 is below BLFS 1.10.7, so link the system libpcap package.
# Everything else links against the system libraries.
%configure --prefix=/usr \
    --without-zenmap \
    --without-ndiff \
    --with-libpcap=yes \
    --with-libpcre=included \
    --with-liblua=included \
    --with-libssh2=included \
    --with-liblinear=included \
    --with-libdnet=included
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/nmap.filelist

%files -n ncat -f %{_sourcedir}/ncat.filelist

%files -n nping -f %{_sourcedir}/nping.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 7.991-1
- New package (BLFS r13.1 Nmap 7.991), split into nmap, ncat and nping.
- Source: https://nmap.org/dist/nmap-7.991.tar.bz2
  md5 a689503c1b7851be8aba804eae414b27
  sha256 a5d507f29437bef3bedd4771ff9aaa8fc1c2a109ddba1f5b1cf12027456929be
- Configure with --without-zenmap --without-ndiff: the Python packaging
  dependencies (pypa-build, setuptools-gettext) are not packaged and the
  graphical frontend is outside this request.
- Link against the packaged libpcap 1.10.7.  Nmap's bundled libpcap is
  1.10.6, below the BLFS 1.10.7 version; the bundled PCRE2 10.47, Lua 5.4.8,
  libssh2 1.11.1_NMAP1 and liblinear 250 are at or above the book versions and
  stay static internals, like vte's bundled subprojects.
- OpenSSL 4 is detected from the system; no openssl4 fixes patch was needed.
