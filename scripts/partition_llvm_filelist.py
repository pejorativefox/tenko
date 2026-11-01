#!/usr/bin/env python3
"""Partition a full LLVM filelist into the Fedora-style subpackage lists.

The input is the output of ``gen_filelist_tree.py`` for the LLVM buildroot
(version 23.1.0, flat /usr layout).  Every entry is assigned to exactly one
package; llvm-all is a meta-package with no payload.

Layout (as close as this build allows to Fedora F44's llvm src.rpm):

  llvm                       LLVM tools and binaries
  llvm-libs                  versioned libLLVM/libLTO/libRemarks + LLVMgold
  llvm-devel                 LLVM headers, CMake, unversioned links, llvm-config
  llvm-static                every .a archive (LLVM, clang and compiler-rt)
  clang                      clang/clang++/clang-23 driver binaries and configs
  clang-libs                 versioned libclang/libclang-cpp
  clang-devel                clang headers, CMake, unversioned links, clang-tblgen
  clang-tools-extra          clang-format/check/refactor/diagtool/c-index-test/...
  clang-analyzer             scan-build/scan-view/analyze-build + libear/libscanbuild
  clang-resource-filesystem  /usr/lib/clang/23 include, share and hwasan_symbolize
  compiler-rt                /usr/lib/clang/23/lib runtimes (non-.a)

Usage:
    ./scripts/partition_llvm_filelist.py --input full.filelist \
        --output-dir package_specs/llvm/files [--check]
"""

import argparse
import os
import sys

PACKAGES = (
    "llvm",
    "llvm-libs",
    "llvm-devel",
    "llvm-static",
    "clang",
    "clang-libs",
    "clang-devel",
    "clang-tools-extra",
    "clang-analyzer",
    "clang-resource-filesystem",
    "compiler-rt",
)

CLANG_CORE_BINS = {
    "clang",
    "clang++",
    "clang-23",
    "clang-cl",
    "clang-cpp",
    "clang-scan-deps",
}

ANALYZER_BINS = {
    "analyze-build",
    "intercept-build",
    "scan-build",
    "scan-build-py",
    "scan-view",
}

# Tools that are neither clang-prefixed nor part of the LLVM core tools.
CLANG_TOOLS_EXTRA_BINS = {
    "amdgpu-arch",
    "c-index-test",
    "diagtool",
    "git-clang-format",
    "hmaptool",
    "nvptx-arch",
    "offload-arch",
}

VERSIONED_LLVM_LIBS = {
    "libLLVM.so.23.1",
    "libLLVM-23.so",
    "libLTO.so.23.1",
    "libRemarks.so.23.1",
    "LLVMgold.so",
}
UNVERSIONED_LLVM_LIBS = {"libLLVM.so", "libLTO.so", "libRemarks.so"}

VERSIONED_CLANG_LIBS = {
    "libclang-cpp.so.23.1",
    "libclang.so.23.1",
    "libclang.so.23.1.0",
}
UNVERSIONED_CLANG_LIBS = {"libclang-cpp.so", "libclang.so"}


def classify(entry):
    """Return the package that owns one filelist entry."""
    path = entry[5:] if entry.startswith("%dir ") else entry

    if path == "/usr/lib":
        return "llvm-libs"

    if path == "/usr/lib/clang" or path.startswith("/usr/lib/clang/"):
        if path in ("/usr/lib/clang", "/usr/lib/clang/23"):
            return "clang-resource-filesystem"
        prefix = "/usr/lib/clang/23/"
        if not path.startswith(prefix):
            raise ValueError("unexpected clang resource path: " + entry)
        rest = path[len(prefix):]
        top = rest.split("/", 1)[0]
        if top in ("include", "share", "bin"):
            return "clang-resource-filesystem"
        if top == "lib":
            if path.endswith(".a"):
                return "llvm-static"
            return "compiler-rt"
        raise ValueError("unassigned clang resource entry: " + entry)

    if path.startswith("/usr/lib/"):
        base = path[len("/usr/lib/"):]
        if path.endswith(".a"):
            return "llvm-static"
        if base == "cmake" or base.startswith("cmake/"):
            if base == "cmake" or base.startswith("cmake/llvm"):
                return "llvm-devel"
            if base.startswith("cmake/clang"):
                return "clang-devel"
            raise ValueError("unassigned cmake entry: " + entry)
        if base in ("libear", "libscanbuild") or base.startswith(
            ("libear/", "libscanbuild/")
        ):
            return "clang-analyzer"
        if base in VERSIONED_LLVM_LIBS:
            return "llvm-libs"
        if base in VERSIONED_CLANG_LIBS:
            return "clang-libs"
        if base in UNVERSIONED_LLVM_LIBS:
            return "llvm-devel"
        if base in UNVERSIONED_CLANG_LIBS:
            return "clang-devel"
        raise ValueError("unassigned /usr/lib entry: " + entry)

    if path == "/usr/include" or path.startswith("/usr/include/llvm"):
        return "llvm-devel"
    if path.startswith("/usr/include/clang"):
        return "clang-devel"
    if path.startswith("/usr/include/"):
        raise ValueError("unassigned include entry: " + entry)

    if path == "/etc/clang" or path.startswith("/etc/clang/"):
        return "clang"

    if path == "/usr/bin":
        return "llvm"
    if path.startswith("/usr/bin/"):
        name = path.rsplit("/", 1)[-1]
        if name in CLANG_CORE_BINS:
            return "clang"
        if name in ANALYZER_BINS:
            return "clang-analyzer"
        if name == "llvm-config":
            return "llvm-devel"
        if name == "clang-tblgen":
            return "clang-devel"
        if name in CLANG_TOOLS_EXTRA_BINS or name.startswith("clang"):
            return "clang-tools-extra"
        return "llvm"

    if path == "/usr/libexec" or path.startswith("/usr/libexec/"):
        return "clang-analyzer"

    if path.startswith("/usr/share/scan-build") or path.startswith(
        "/usr/share/scan-view"
    ):
        return "clang-analyzer"
    if path == "/usr/share" or path.startswith("/usr/share/man"):
        return "llvm"
    if path.startswith("/usr/share/clang"):
        return "clang-tools-extra"
    if path.startswith("/usr/share/opt-viewer"):
        return "llvm"
    if path.startswith("/usr/share/"):
        raise ValueError("unassigned share entry: " + entry)

    raise ValueError("unassigned entry: " + entry)


def read_list(path):
    with open(path, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="full generated filelist")
    ap.add_argument(
        "--output-dir",
        default="package_specs/llvm/files",
        help="directory holding the per-package filelists",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="verify existing lists instead of writing them",
    )
    args = ap.parse_args()

    full = read_list(args.input)
    if len(full) != len(set(full)):
        sys.exit("duplicate entries in " + args.input)

    buckets = {name: [] for name in PACKAGES}
    for entry in full:
        buckets[classify(entry)].append(entry)

    total = sum(len(v) for v in buckets.values())
    if total != len(full):
        sys.exit("partition {} entries, input has {}".format(total, len(full)))

    if args.check:
        failed = False
        for name in PACKAGES:
            path = os.path.join(args.output_dir, name + ".filelist")
            existing = read_list(path)
            if existing != buckets[name]:
                print("MISMATCH: {}".format(path))
                failed = True
            else:
                print("{}: {} entries".format(name, len(existing)))
        if set(full) != set().union(*(set(v) for v in buckets.values())):
            print("MISMATCH: partition is not the input set")
            failed = True
        return 1 if failed else 0

    os.makedirs(args.output_dir, exist_ok=True)
    for name in PACKAGES:
        path = os.path.join(args.output_dir, name + ".filelist")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(buckets[name]) + "\n")
        print("{}: {} entries".format(path, len(buckets[name])))
    print("total: {} entries".format(total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
