Name:       lgi
Version:    0.9.2
Release:    1
Summary:    Lua bindings for GObject Introspection
License:    MIT
Prefix:     /usr
URL:        https://github.com/lgi-devs/lgi
Source0:    %{name}-%{version}.tar.gz
Patch1:     %{name}-%{version}-lua54.patch
Patch2:     %{name}-%{version}-glib286-enums.patch
BuildRequires: gobject-introspection

%description
LGI is a gobject-introspection based dynamic Lua binding for GObject
based libraries.  It allows using GObject based libraries, such as GTK
and GStreamer, from Lua.

%prep
%setup -q
%patch -P 1 -p1
%patch -P 2 -p1

%build
%make_build PREFIX=/usr LUA_VERSION=5.4

%install
rm -rf %{buildroot}
make install PREFIX=/usr LUA_VERSION=5.4 DESTDIR=%{buildroot}

%files -f %{_sourcedir}/lgi.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.9.2-1
- Update to 0.9.2; not in the base set, latest upstream
  stable 2026-11-05 (latest tag 0.9.2).
- Build for the documented Lua 5.4 (LUA_VERSION=5.4); the upstream
  Makefile still defaults to 5.1.
- Add the upstream Lua 5.4 build fix (lgi-devs/lgi commit
  5cfd42c386d3), which is not part of the 0.9.2 tag: lua_resume()
  gained a fourth argument in Lua 5.4.
- Add the upstream enum loading fix (lgi-devs/lgi commit
  64016a99a048, issue #358) for GLib >= 2.86: GObject.TypeClass.ref()
  is deprecated in favour of .get() and EnumClass.values is exposed as
  a Lua list instead of a C array.  Without it lgi.cairo fails with
  "bad argument #1 to 'fromarray' (lgi.record expected, got table)".
- Build from the upstream GitHub archive; the extracted top
  directory is lgi-0.9.2.
