Name:       flac
Version:    1.5.0
Release:    2
Summary:    Free Lossless Audio Codec
License:    BSD-3-Clause AND GPL-2.0-or-later AND LGPL-2.1-or-later
URL:        https://github.com/xiph/flac
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz


%description
FLAC is open source software that can reduce the amount of storage space
needed to store digital audio signals without needing to remove information
in doing so. It includes the libFLAC and libFLAC++ libraries, the flac and
metaflac command line tools, and documentation.

%prep
%setup -a 0 

%build
%configure  --disable-thorough-tests
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/flac.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.5.0-2
- Replace the TODO summary/description and record the verified license
  (BSD-3-Clause AND GPL-2.0-or-later AND LGPL-2.1-or-later): README.md (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.5.0-1
- Sync with the base set

# let's skip this for now

