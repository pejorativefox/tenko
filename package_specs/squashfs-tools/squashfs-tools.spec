Name:       squashfs-tools
Version:    4.7.5
Release:    1
Summary:    Tools to create and extract Squashfs filesystems
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: zlib, lz4, xz-devel, zstd, gcc, make

%description
Squashfs-tools provides mksquashfs, unsquashfs, sqfscat and sqfstar for
creating and extracting Squashfs filesystems.  The Browneye live/installer
image uses mksquashfs to build the compressed root filesystem that the
installer unpacks and writes.

This package is a user-approved exception to the LFS/BLFS version-parity
rule: squashfs-tools is not in either book, so it tracks current upstream.
Source: https://github.com/plougher/squashfs-tools/releases/download/4.7.5/squashfs-tools-4.7.5.tar.gz
sha256: 547b7b7f4d2e44bf91b6fc554664850c69563701deab9fd9cd7e21f694c88ea6

%prep
%setup -q

%build
pushd squashfs-tools
%make_build GZIP_SUPPORT=1 LZ4_SUPPORT=1 XZ_SUPPORT=1 ZSTD_SUPPORT=1 \
             LZO_SUPPORT=0 LZMA_SUPPORT=0
popd

%install
rm -rf %{buildroot}
pushd squashfs-tools
install -d %{buildroot}%{_bindir} %{buildroot}%{_mandir}/man1
install -m 755 mksquashfs unsquashfs %{buildroot}%{_bindir}/
ln -sf unsquashfs %{buildroot}%{_bindir}/sqfscat
ln -sf mksquashfs %{buildroot}%{_bindir}/sqfstar
install -m 644 ../Documentation/manpages/mksquashfs.1 \
               ../Documentation/manpages/unsquashfs.1 \
               ../Documentation/manpages/sqfscat.1 \
               ../Documentation/manpages/sqfstar.1 \
               %{buildroot}%{_mandir}/man1/
popd

%files -f %{_sourcedir}/squashfs-tools.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.7.5-1
- Update to upstream 4.7.5 (approved exception; not in LFS/BLFS), replacing
  the 2019 4.4 template.  Enable gzip/lz4/xz/zstd, disable lzo/lzma because
  those libraries are not in the Browneye repo.
- Source sha256: 547b7b7f4d2e44bf91b6fc554664850c69563701deab9fd9cd7e21f694c88ea6
- Install man pages under /usr/share/man (upstream defaults to /usr/man)
