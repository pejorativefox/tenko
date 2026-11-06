Name:       gstreamer
Version:    1.28.8
Release:    2
Summary:    Streaming multimedia framework
License:    LGPL-2.1-or-later AND BSD-3-Clause
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Streaming multimedia framework

%prep
%setup

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -D gst_debug=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files
/usr/bin/gst-inspect-1.0
/usr/bin/gst-launch-1.0
/usr/bin/gst-stats-1.0
/usr/bin/gst-tester-1.0
/usr/bin/gst-typefind-1.0
/usr/include/gstreamer-1.0/gst/base/base-prelude.h
/usr/include/gstreamer-1.0/gst/base/base.h
/usr/include/gstreamer-1.0/gst/base/gstadapter.h
/usr/include/gstreamer-1.0/gst/base/gstaggregator.h
/usr/include/gstreamer-1.0/gst/base/gstbaseparse.h
/usr/include/gstreamer-1.0/gst/base/gstbasesink.h
/usr/include/gstreamer-1.0/gst/base/gstbasesrc.h
/usr/include/gstreamer-1.0/gst/base/gstbasetransform.h
/usr/include/gstreamer-1.0/gst/base/gstbitreader.h
/usr/include/gstreamer-1.0/gst/base/gstbitwriter.h
/usr/include/gstreamer-1.0/gst/base/gstbytereader.h
/usr/include/gstreamer-1.0/gst/base/gstbytewriter.h
/usr/include/gstreamer-1.0/gst/base/gstcollectpads.h
/usr/include/gstreamer-1.0/gst/base/gstdataqueue.h
/usr/include/gstreamer-1.0/gst/base/gstflowcombiner.h
/usr/include/gstreamer-1.0/gst/base/gstpushsrc.h
/usr/include/gstreamer-1.0/gst/base/gstqueuearray.h
/usr/include/gstreamer-1.0/gst/base/gsttypefindhelper.h
/usr/include/gstreamer-1.0/gst/check/check-prelude.h
/usr/include/gstreamer-1.0/gst/check/check.h
/usr/include/gstreamer-1.0/gst/check/gstbufferstraw.h
/usr/include/gstreamer-1.0/gst/check/gstcheck.h
/usr/include/gstreamer-1.0/gst/check/gstconsistencychecker.h
/usr/include/gstreamer-1.0/gst/check/gstharness.h
/usr/include/gstreamer-1.0/gst/check/gsttestclock.h
/usr/include/gstreamer-1.0/gst/check/internal-check.h
/usr/include/gstreamer-1.0/gst/controller/controller-enumtypes.h
/usr/include/gstreamer-1.0/gst/controller/controller-prelude.h
/usr/include/gstreamer-1.0/gst/controller/controller.h
/usr/include/gstreamer-1.0/gst/controller/gstargbcontrolbinding.h
/usr/include/gstreamer-1.0/gst/controller/gstdirectcontrolbinding.h
/usr/include/gstreamer-1.0/gst/controller/gstinterpolationcontrolsource.h
/usr/include/gstreamer-1.0/gst/controller/gstlfocontrolsource.h
/usr/include/gstreamer-1.0/gst/controller/gstproxycontrolbinding.h
/usr/include/gstreamer-1.0/gst/controller/gsttimedvaluecontrolsource.h
/usr/include/gstreamer-1.0/gst/controller/gsttriggercontrolsource.h
/usr/include/gstreamer-1.0/gst/glib-compat.h
/usr/include/gstreamer-1.0/gst/gst.h
/usr/include/gstreamer-1.0/gst/gstallocator.h
/usr/include/gstreamer-1.0/gst/gstatomicqueue.h
/usr/include/gstreamer-1.0/gst/gstbin.h
/usr/include/gstreamer-1.0/gst/gstbuffer.h
/usr/include/gstreamer-1.0/gst/gstbufferlist.h
/usr/include/gstreamer-1.0/gst/gstbufferpool.h
/usr/include/gstreamer-1.0/gst/gstbus.h
/usr/include/gstreamer-1.0/gst/gstbytearrayinterface.h
/usr/include/gstreamer-1.0/gst/gstcaps.h
/usr/include/gstreamer-1.0/gst/gstcapsfeatures.h
/usr/include/gstreamer-1.0/gst/gstchildproxy.h
/usr/include/gstreamer-1.0/gst/gstclock.h
/usr/include/gstreamer-1.0/gst/gstcompat.h
/usr/include/gstreamer-1.0/gst/gstconfig.h
/usr/include/gstreamer-1.0/gst/gstcontext.h
/usr/include/gstreamer-1.0/gst/gstcontrolbinding.h
/usr/include/gstreamer-1.0/gst/gstcontrolsource.h
/usr/include/gstreamer-1.0/gst/gstcpuid.h
/usr/include/gstreamer-1.0/gst/gstdatetime.h
/usr/include/gstreamer-1.0/gst/gstdebugutils.h
/usr/include/gstreamer-1.0/gst/gstdevice.h
/usr/include/gstreamer-1.0/gst/gstdevicemonitor.h
/usr/include/gstreamer-1.0/gst/gstdeviceprovider.h
/usr/include/gstreamer-1.0/gst/gstdeviceproviderfactory.h
/usr/include/gstreamer-1.0/gst/gstdynamictypefactory.h
/usr/include/gstreamer-1.0/gst/gstelement.h
/usr/include/gstreamer-1.0/gst/gstelementfactory.h
/usr/include/gstreamer-1.0/gst/gstelementmetadata.h
/usr/include/gstreamer-1.0/gst/gstenumtypes.h
/usr/include/gstreamer-1.0/gst/gsterror.h
/usr/include/gstreamer-1.0/gst/gstevent.h
/usr/include/gstreamer-1.0/gst/gstformat.h
/usr/include/gstreamer-1.0/gst/gstghostpad.h
/usr/include/gstreamer-1.0/gst/gstidstr.h
/usr/include/gstreamer-1.0/gst/gstinfo.h
/usr/include/gstreamer-1.0/gst/gstiterator.h
/usr/include/gstreamer-1.0/gst/gstmacros.h
/usr/include/gstreamer-1.0/gst/gstmemory.h
/usr/include/gstreamer-1.0/gst/gstmessage.h
/usr/include/gstreamer-1.0/gst/gstmeta.h
/usr/include/gstreamer-1.0/gst/gstmetafactory.h
/usr/include/gstreamer-1.0/gst/gstminiobject.h
/usr/include/gstreamer-1.0/gst/gstobject.h
/usr/include/gstreamer-1.0/gst/gstpad.h
/usr/include/gstreamer-1.0/gst/gstpadtemplate.h
/usr/include/gstreamer-1.0/gst/gstparamspecs.h
/usr/include/gstreamer-1.0/gst/gstparse.h
/usr/include/gstreamer-1.0/gst/gstpipeline.h
/usr/include/gstreamer-1.0/gst/gstplugin.h
/usr/include/gstreamer-1.0/gst/gstpluginfeature.h
/usr/include/gstreamer-1.0/gst/gstpoll.h
/usr/include/gstreamer-1.0/gst/gstpreset.h
/usr/include/gstreamer-1.0/gst/gstpromise.h
/usr/include/gstreamer-1.0/gst/gstprotection.h
/usr/include/gstreamer-1.0/gst/gstquery.h
/usr/include/gstreamer-1.0/gst/gstregistry.h
/usr/include/gstreamer-1.0/gst/gstsample.h
/usr/include/gstreamer-1.0/gst/gstsegment.h
/usr/include/gstreamer-1.0/gst/gststreamcollection.h
/usr/include/gstreamer-1.0/gst/gststreams.h
/usr/include/gstreamer-1.0/gst/gststructure.h
/usr/include/gstreamer-1.0/gst/gstsystemclock.h
/usr/include/gstreamer-1.0/gst/gsttaglist.h
/usr/include/gstreamer-1.0/gst/gsttagsetter.h
/usr/include/gstreamer-1.0/gst/gsttask.h
/usr/include/gstreamer-1.0/gst/gsttaskpool.h
/usr/include/gstreamer-1.0/gst/gsttoc.h
/usr/include/gstreamer-1.0/gst/gsttocsetter.h
/usr/include/gstreamer-1.0/gst/gsttracer.h
/usr/include/gstreamer-1.0/gst/gsttracerfactory.h
/usr/include/gstreamer-1.0/gst/gsttracerrecord.h
/usr/include/gstreamer-1.0/gst/gsttypefind.h
/usr/include/gstreamer-1.0/gst/gsttypefindfactory.h
/usr/include/gstreamer-1.0/gst/gsturi.h
/usr/include/gstreamer-1.0/gst/gstutils.h
/usr/include/gstreamer-1.0/gst/gstvalue.h
/usr/include/gstreamer-1.0/gst/gstvecdeque.h
/usr/include/gstreamer-1.0/gst/gstversion.h
/usr/include/gstreamer-1.0/gst/math-compat.h
/usr/include/gstreamer-1.0/gst/net/gstnet.h
/usr/include/gstreamer-1.0/gst/net/gstnetaddressmeta.h
/usr/include/gstreamer-1.0/gst/net/gstnetclientclock.h
/usr/include/gstreamer-1.0/gst/net/gstnetcontrolmessagemeta.h
/usr/include/gstreamer-1.0/gst/net/gstnettimepacket.h
/usr/include/gstreamer-1.0/gst/net/gstnettimeprovider.h
/usr/include/gstreamer-1.0/gst/net/gstnetutils.h
/usr/include/gstreamer-1.0/gst/net/gstptpclock.h
/usr/include/gstreamer-1.0/gst/net/net-prelude.h
/usr/include/gstreamer-1.0/gst/net/net.h
/usr/lib64/girepository-1.0/Gst-1.0.typelib
/usr/lib64/girepository-1.0/GstBase-1.0.typelib
/usr/lib64/girepository-1.0/GstCheck-1.0.typelib
/usr/lib64/girepository-1.0/GstController-1.0.typelib
/usr/lib64/girepository-1.0/GstNet-1.0.typelib
/usr/lib64/gstreamer-1.0/libgstcoreelements.so
/usr/lib64/gstreamer-1.0/libgstcoretracers.so
/usr/lib64/libgstbase-1.0.so
/usr/lib64/libgstbase-1.0.so.0
/usr/lib64/libgstbase-1.0.so.0.2808.0
/usr/lib64/libgstcheck-1.0.so
/usr/lib64/libgstcheck-1.0.so.0
/usr/lib64/libgstcheck-1.0.so.0.2808.0
/usr/lib64/libgstcontroller-1.0.so
/usr/lib64/libgstcontroller-1.0.so.0
/usr/lib64/libgstcontroller-1.0.so.0.2808.0
/usr/lib64/libgstnet-1.0.so
/usr/lib64/libgstnet-1.0.so.0
/usr/lib64/libgstnet-1.0.so.0.2808.0
/usr/lib64/libgstreamer-1.0.so
/usr/lib64/libgstreamer-1.0.so.0
/usr/lib64/libgstreamer-1.0.so.0.2808.0
/usr/lib64/pkgconfig/gstreamer-1.0.pc
/usr/lib64/pkgconfig/gstreamer-base-1.0.pc
/usr/lib64/pkgconfig/gstreamer-check-1.0.pc
/usr/lib64/pkgconfig/gstreamer-controller-1.0.pc
/usr/lib64/pkgconfig/gstreamer-net-1.0.pc
/usr/libexec/gstreamer-1.0/gst-completion-helper
/usr/libexec/gstreamer-1.0/gst-hotdoc-plugins-scanner
/usr/libexec/gstreamer-1.0/gst-plugin-scanner
/usr/libexec/gstreamer-1.0/gst-plugins-doc-cache-generator
/usr/share/aclocal/gst-element-check-1.0.m4
/usr/share/cmake/FindGStreamer.cmake
/usr/share/gdb/auto-load/usr/lib64/libgstreamer-1.0.so.0.2808.0-gdb.py
/usr/share/gir-1.0/Gst-1.0.gir
/usr/share/gir-1.0/GstBase-1.0.gir
/usr/share/gir-1.0/GstCheck-1.0.gir
/usr/share/gir-1.0/GstController-1.0.gir
/usr/share/gir-1.0/GstNet-1.0.gir
/usr/share/gstreamer-1.0/gdb/glib_gobject_helper.py
/usr/share/gstreamer-1.0/gdb/gst_gdb.py
/usr/share/locale/af/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/ar/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/ast/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/az/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/be/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/bg/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/ca/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/cs/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/da/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/de/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/el/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/en_GB/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/eo/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/es/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/eu/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/fi/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/fr/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/fur/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/gl/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/hr/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/hu/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/id/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/it/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/ja/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/ka/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/kk/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/ko/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/lt/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/lv/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/nb/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/nl/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/pl/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/pt_BR/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/ro/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/ru/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/rw/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/sk/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/sl/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/sq/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/sr/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/sv/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/tr/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/uk/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/vi/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/zh_CN/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/locale/zh_TW/LC_MESSAGES/gstreamer-1.0.mo
/usr/share/man/man1/gst-inspect-1.0.1.gz
/usr/share/man/man1/gst-launch-1.0.1.gz
/usr/share/man/man1/gst-stats-1.0.1.gz
/usr/share/man/man1/gst-typefind-1.0.1.gz

/usr/libexec/gstreamer-1.0/gst-ptp-helper

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.28.8-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later AND BSD-3-Clause): COPYING, gst/gstplugin.c and gst/gstcpuid.c (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.28.8-1
- Sync with the base set

* Thu Sep 10 2020 Chris Statzer <chris.statzer@qq.com> 1.16.2
- Initial RPM

