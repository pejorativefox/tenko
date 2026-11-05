Name:       libsigc++
Version:    2.12.1
Release:    2
Summary:    libsigc++ provides a typesafe (at compile time) callback system for standard C++.
License:    LGPL-2.1-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
libsigc++ provides a typesafe (at compile time) callback system for standard C++.

%prep
%setup

%build
sed -i "s/'system',//" meson.build
mkdir bld
pushd bld
meson setup --prefix=/usr --buildtype=release ..
ninja
popd

%install
rm -rf %{buildroot}
pushd bld
DESTDIR=%{buildroot} ninja install
popd

%files
/usr/include/sigc++-2.0/sigc++/adaptors/adaptor_trait.h
/usr/include/sigc++-2.0/sigc++/adaptors/adaptors.h
/usr/include/sigc++-2.0/sigc++/adaptors/bind.h
/usr/include/sigc++-2.0/sigc++/adaptors/bind_return.h
/usr/include/sigc++-2.0/sigc++/adaptors/bound_argument.h
/usr/include/sigc++-2.0/sigc++/adaptors/compose.h
/usr/include/sigc++-2.0/sigc++/adaptors/deduce_result_type.h
/usr/include/sigc++-2.0/sigc++/adaptors/exception_catch.h
/usr/include/sigc++-2.0/sigc++/adaptors/hide.h
/usr/include/sigc++-2.0/sigc++/adaptors/lambda/base.h
/usr/include/sigc++-2.0/sigc++/adaptors/lambda/select.h
/usr/include/sigc++-2.0/sigc++/adaptors/retype.h
/usr/include/sigc++-2.0/sigc++/adaptors/retype_return.h
/usr/include/sigc++-2.0/sigc++/adaptors/track_obj.h
/usr/include/sigc++-2.0/sigc++/bind.h
/usr/include/sigc++-2.0/sigc++/bind_return.h
/usr/include/sigc++-2.0/sigc++/connection.h
/usr/include/sigc++-2.0/sigc++/functors/functor_trait.h
/usr/include/sigc++-2.0/sigc++/functors/functors.h
/usr/include/sigc++-2.0/sigc++/functors/mem_fun.h
/usr/include/sigc++-2.0/sigc++/functors/ptr_fun.h
/usr/include/sigc++-2.0/sigc++/functors/slot.h
/usr/include/sigc++-2.0/sigc++/functors/slot_base.h
/usr/include/sigc++-2.0/sigc++/limit_reference.h
/usr/include/sigc++-2.0/sigc++/reference_wrapper.h
/usr/include/sigc++-2.0/sigc++/retype_return.h
/usr/include/sigc++-2.0/sigc++/sigc++.h
/usr/include/sigc++-2.0/sigc++/signal.h
/usr/include/sigc++-2.0/sigc++/signal_base.h
/usr/include/sigc++-2.0/sigc++/slot.h
/usr/include/sigc++-2.0/sigc++/trackable.h
/usr/include/sigc++-2.0/sigc++/type_traits.h
/usr/include/sigc++-2.0/sigc++/visit_each.h
/usr/lib64/libsigc-2.0.so
/usr/lib64/libsigc-2.0.so.0
/usr/lib64/libsigc-2.0.so.0.0.0
/usr/lib64/pkgconfig/sigc++-2.0.pc
/usr/lib64/sigc++-2.0/include/sigc++config.h

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.12.1-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): COPYING, plus sigc++/*.h "version 2.1 ... or any later version" (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.12.1-1
- Sync with BLFS r13.1

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 2.10.3
- Initial RPM

