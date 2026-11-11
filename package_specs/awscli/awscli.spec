# AWS CLI v2 ships as an official self-contained linux-x86_64 bundle: the aws
# and aws_completer executables, libpython, the CLI/botocore modules and the
# Python libraries they need.  This is a binary repackage, not a source build.
#
# aws-cli is not part of the base set.  The user asked for this package; the
# v2 bundle is Amazon's current stable release (v1 is maintenance-only).
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

# ~270 MiB installed; xz level 6 keeps the RPM near the 72 MiB upstream zip
# without a large packaging cost.
%global _binary_payload w6.xzdio

Name:       awscli
Version:    2.40.0
Release:    1
Summary:    AWS Command Line Interface v2 (official prebuilt linux-x86_64 bundle)
License:    Apache-2.0
URL:        https://aws.amazon.com/cli/
Prefix:     /opt

# 2.40.0 bundle, 74898367 bytes
#   sha256 4a6d34150060a6bc30160ef1f66e536db64674797bbb582044f93bb9c6e299e7
#   md5    cc271601d28b7ecf835b0bd03c0a2d13  (also in ./sources)
Source0:    awscli-exe-linux-x86_64-%{version}.zip
# The bundle has no license file; this is the Apache-2.0 notice from the
# matching aws-cli source release.
Source1:    LICENSE

ExclusiveArch: x86_64

BuildRequires: unzip

# Prebuilt payload: never let rpm guess provides/requires from the bundled
# libraries under /opt.  The explicit runtime list below is the real host
# requirement; Python, botocore and the compression/readline libraries are
# bundled in dist/.
AutoProv: no
AutoReq: no

Provides:   aws-cli = %{version}-%{release}

Requires:   glibc >= 2.17
Requires:   zlib
# /etc/ssl/certs for the default TLS trust store.
Requires:   make-ca

%description
The AWS Command Line Interface is a unified tool for managing Amazon Web
Services from the command line.

This package repackages the official AWS CLI v2 linux-x86_64 bundle under
/opt/awscli-%{version} (with /opt/awscli as a stable symlink and
/usr/bin/aws and /usr/bin/aws_completer as the PATH entry points).  The
bundle is self-contained: it ships its own Python 3.14 runtime, botocore,
s3transfer, docutils and awscrt.

The AWS CLI v2 is distributed only as this bundled installer, not as a
source release on PyPI; v1 is in maintenance mode.  awscli is not in the
base set.

%prep
%setup -q -c -n %{name}-%{version}

%build

%install
rm -rf %{buildroot}

install -d %{buildroot}/opt/awscli-%{version}/bin
install -d %{buildroot}/opt/awscli-%{version}/dist
cp -a aws/dist/. %{buildroot}/opt/awscli-%{version}/dist/
ln -s ../dist/aws %{buildroot}/opt/awscli-%{version}/bin/aws
ln -s ../dist/aws_completer %{buildroot}/opt/awscli-%{version}/bin/aws_completer
ln -s awscli-%{version} %{buildroot}/opt/awscli

install -d %{buildroot}%{_bindir}
ln -s /opt/awscli/bin/aws %{buildroot}%{_bindir}/aws
ln -s /opt/awscli/bin/aws_completer %{buildroot}%{_bindir}/aws_completer

install -d %{buildroot}%{_docdir}/awscli
install -m644 %{SOURCE1} %{buildroot}%{_docdir}/awscli/LICENSE
install -m644 aws/README.md %{buildroot}%{_docdir}/awscli/README.md
install -m644 aws/THIRD_PARTY_LICENSES \
    %{buildroot}%{_docdir}/awscli/THIRD_PARTY_LICENSES

%files -f %{_sourcedir}/awscli.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 2.40.0-1
- New package: the official AWS CLI v2.40.0 linux-x86_64 bundle under
  /opt/awscli-2.40.0, with /opt/awscli, /usr/bin/aws and
  /usr/bin/aws_completer symlinks (latest stable upstream release,
  checked 2026-11-11).
- awscli is not in the base set; v2 is distributed only as the bundled
  installer, so this is a prebuilt binary package.
