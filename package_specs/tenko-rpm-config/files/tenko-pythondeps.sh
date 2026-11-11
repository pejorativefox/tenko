#!/bin/sh
# tenko-pythondeps.sh --provides|--requires
# Read file paths on stdin (from rpm's python fileattr) and print
# python(abi) dependencies.  See python.attr.  rpm passes absolute paths
# inside the buildroot, so strip $RPM_BUILD_ROOT first.
case "$1" in
    --provides) pattern='^/usr/bin/python([0-9]+\.[0-9]+)$' ;;
    --requires) pattern='^/usr/lib(64)?/python([0-9]+\.[0-9]+)/' ;;
    *) echo "usage: $0 --provides|--requires" >&2; exit 2 ;;
esac
sed "s|^${RPM_BUILD_ROOT%/}||" | grep -E "$pattern" | sed -E 's#^/usr/(bin|lib(64)?)/python([0-9]+\.[0-9]+).*#python(abi) = \3#' | sort -u
