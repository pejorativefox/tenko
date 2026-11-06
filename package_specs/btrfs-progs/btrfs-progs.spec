Name:       btrfs-progs
Version:    7.3
Release:    1
Summary:    B-tree filesystem administration and debugging tools
License:    GPL-2.0-only AND LGPL-2.1-or-later
Source0:    %{name}-v%{version}.tar.xz
Prefix:     /usr

%description
The btrfs-progs package contains administration and debugging tools for
the B-tree file system (btrfs), including mkfs.btrfs, fsck.btrfs, btrfs
and btrfstune.

%prep
%setup -q -n %{name}-v%{version}

%build
%configure --disable-static \
           --disable-documentation
%make_build

%install
rm -rf %{buildroot}
%make_install
# --disable-documentation skips the sphinx build; the base build installs the
# pre-generated manual pages by hand.
for i in 5 8; do
    install -d %{buildroot}%{_mandir}/man$i
    install -m644 Documentation/*.$i %{buildroot}%{_mandir}/man$i/
done

%files -f %{_sourcedir}/btrfs-progs.filelist

%changelog
* Fri Nov 06 2026 browneye <build@browneye.invalid> 7.3-1
- Add btrfs-progs 7.3 from the base set
  postlfs/filesystems/btrfs-progs.xml for the installer's btrfs support.
- Configure as documented: --disable-static --disable-documentation.
  Install the pre-generated manual pages from Documentation/ as the base build
  describes.  The package links against liblzo2 2.10 from
  general/genlib/lzo.xml.
- The kernel already provides btrfs (CONFIG_BTRFS_FS=y), so no kernel
  change is needed.
- Record the verified license (GPL-2.0-only AND LGPL-2.1-or-later):
  COPYING, the GPL-2.0-only program headers and libbtrfsutil/COPYING.
- Ship a generated static filelist.
