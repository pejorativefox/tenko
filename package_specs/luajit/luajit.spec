Name:       luajit
Version:    20260213
Release:    1
Summary:    Just-In-Time compiler for the Lua language
License:    MIT
URL:        https://luajit.org/
Source0:    luajit-%{version}.tar.xz
Prefix:     /usr

%description
LuaJIT is a Just-In-Time compiler for the Lua programming language.  It
implements the Lua 5.1 language and API with an FFI extension and is
compatible with the de-facto LuaJIT 2.1 ABI used by mpv's scripting
interface.

LuaJIT has rolling releases and does not publish versioned tarballs; this
package is the 2026-02-13 snapshot used by BLFS r13.1.

%prep
%setup -q

%build
make %{?_smp_mflags} PREFIX=/usr amalg

%install
rm -rf %{buildroot}
make PREFIX=/usr DESTDIR=%{buildroot} install
rm -vf %{buildroot}/usr/lib/libluajit-5.1.a
rm -rf %{buildroot}/usr/lib/lua %{buildroot}/usr/share/lua

%files
%dir /usr/include/luajit-2.1
/usr/include/luajit-2.1/lauxlib.h
/usr/include/luajit-2.1/lua.h
/usr/include/luajit-2.1/lua.hpp
/usr/include/luajit-2.1/luaconf.h
/usr/include/luajit-2.1/luajit.h
/usr/include/luajit-2.1/lualib.h
/usr/bin/luajit
/usr/bin/luajit-2.1.ROLLING
/usr/lib/libluajit-5.1.so
/usr/lib/libluajit-5.1.so.2
/usr/lib/libluajit-5.1.so.2.1.ROLLING
/usr/lib/pkgconfig/luajit.pc
%dir /usr/share/luajit-2.1
%dir /usr/share/luajit-2.1/jit
/usr/share/luajit-2.1/jit/bc.lua
/usr/share/luajit-2.1/jit/bcsave.lua
/usr/share/luajit-2.1/jit/dis_arm.lua
/usr/share/luajit-2.1/jit/dis_arm64.lua
/usr/share/luajit-2.1/jit/dis_arm64be.lua
/usr/share/luajit-2.1/jit/dis_mips.lua
/usr/share/luajit-2.1/jit/dis_mips64.lua
/usr/share/luajit-2.1/jit/dis_mips64el.lua
/usr/share/luajit-2.1/jit/dis_mips64r6.lua
/usr/share/luajit-2.1/jit/dis_mips64r6el.lua
/usr/share/luajit-2.1/jit/dis_mipsel.lua
/usr/share/luajit-2.1/jit/dis_ppc.lua
/usr/share/luajit-2.1/jit/dis_x64.lua
/usr/share/luajit-2.1/jit/dis_x86.lua
/usr/share/luajit-2.1/jit/dump.lua
/usr/share/luajit-2.1/jit/p.lua
/usr/share/luajit-2.1/jit/v.lua
/usr/share/luajit-2.1/jit/vmdef.lua
/usr/share/luajit-2.1/jit/zone.lua
/usr/share/man/man1/luajit.1.gz

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 20260213-1
- New package: LuaJIT 2.1 rolling snapshot 20260213 from BLFS r13.1,
  the latest snapshot the book ships.  LuaJIT is required by mpv 0.42,
  whose scripting interface only supports Lua 5.1/LuaJIT or Lua 5.2,
  while the base system ships Lua 5.4.
