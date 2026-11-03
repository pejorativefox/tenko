# Liberation fonts are referenced from the BLFS TTF-and-OTF-fonts page but
# the book does not carry a versioned download entity for them.  2.1.5 is the
# current upstream release (GitHub tag 2.1.5).  The user explicitly requested
# the package, so this is a user-approved exception to the version-parity rule.
#
# The -ttf tarball is the upstream ready-made font artifact: no build step.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       liberation-fonts
Version:    2.1.5
Release:    1
Summary:    Metric-compatible substitutes for Arial, Courier New and Times New Roman
License:    OFL-1.1
URL:        https://github.com/liberationfonts/liberation-fonts
Prefix:     /usr
Source0:    liberation-fonts-ttf-%{version}.tar.gz

ExclusiveArch: x86_64

AutoProv: no
AutoReq: no

%description
The Liberation fonts provide libre, metric-compatible substitutes for
Arial, Courier New and Times New Roman.  Fontconfig will use them when
those fonts are requested, and also for the similar Helvetica, Courier and
Times Roman families.

BLFS documents the Liberation fonts in its TTF-and-OTF-fonts page but does
not provide a versioned download entity; 2.1.5 is the current upstream
release.  This package ships the upstream ready-made TTF artifact together
with its OFL license and README.  User-approved exception for browneye.

%prep
%setup -q -n liberation-fonts-ttf-%{version}

%build

%install
rm -rf %{buildroot}
install -d -m 0755 %{buildroot}/usr/share/fonts/liberation-fonts
install -m 0644 liberation-fonts-ttf-%{version}/*.ttf \
    %{buildroot}/usr/share/fonts/liberation-fonts/
install -m 0644 liberation-fonts-ttf-%{version}/LICENSE \
    %{buildroot}/usr/share/fonts/liberation-fonts/LICENSE
install -m 0644 liberation-fonts-ttf-%{version}/README.md \
    %{buildroot}/usr/share/fonts/liberation-fonts/README.md

%files -f %{_sourcedir}/liberation-fonts.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.1.5-1
- Initial package: upstream Liberation fonts 2.1.5 TTF artifact, with the
  OFL license text.  BLFS references the fonts without a versioned entity;
  user-approved exception.
