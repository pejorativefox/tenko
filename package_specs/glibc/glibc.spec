Name:       glibc
Version:    2.44
Release:    1
Summary:    Provides the GNU glibc library
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

Provides: rtld(GNU_HASH)

%description
TODO
kluged to work around: https://www.linuxquestions.org/questions/slackware-14/bug-while-building-glibc-2-27-with-new-gcc-8-1-1-and-perl-5-28-0-a-4175632782/


%prep
%setup -q

%build
export CFLAGS="-O2 -g"
export CXXFLAGS="-O2 -g"
export LDFLAGS=""
patch -Np1 -i %{_sourcedir}/glibc-fhs-1.patch
patch -Np1 -i %{_sourcedir}/glibc-2.44-upstream_fixes-1.patch

mkdir build
pushd build
../configure --prefix=/usr                            \
             --disable-werror                         \
             --disable-nscd                           \
             --without-selinux                        \
             libc_cv_slibdir=/usr/lib64               \
             --enable-kernel=5.10                     \
             --enable-stack-protector=strong
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
sed '/test-installation/s@$(PERL)@echo not running@' -i ../Makefile
make -j%{_smp_build_ncpus} install_root=%{buildroot} install
if [ -d %{buildroot}/sbin ]; then mkdir -p %{buildroot}/usr/sbin; mv %{buildroot}/sbin/* %{buildroot}/usr/sbin/; rmdir %{buildroot}/sbin; fi
sed '/RTLDLIST=/s@/usr@@g' -i %{buildroot}/usr/bin/ldd
popd

cp -v nscd/nscd.conf %{buildroot}/etc/nscd.conf
mkdir -pv %{buildroot}/var/cache/nscd
touch %{buildroot}/var/cache/nscd/.keep

mkdir -pv %{buildroot}/etc
cat > %{buildroot}/etc/nsswitch.conf << "EOF"
# Begin /etc/nsswitch.conf

passwd: files
group: files
shadow: files

hosts: files dns
networks: files

protocols: files
services: files
ethers: files
rpc: files

# End /etc/nsswitch.conf
EOF

mkdir -pv %{buildroot}/etc/ld.so.conf.d/
cat >> %{buildroot}/etc/ld.so.conf << "EOF"
# Add an include directory
include /etc/ld.so.conf.d/*.conf
/usr/local/lib
/opt/lib

EOF
mkdir -pv %{buildroot}/etc/ld.so.conf.d
touch %{buildroot}/etc/ld.so.conf.d/.keep

%files
/etc/
/usr/libexec/
/var/
/usr/bin/
/usr/include/
/usr/lib/
/usr/lib64/
/usr/sbin/
/usr/share/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.44
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 2.38
- Version bump
