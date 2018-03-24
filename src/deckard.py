#!/usr/bin/env python3

import sys
import IPython

import androguard.misc

def to_dalvik_notation(name):
    return "L{0};".format(name.replace(".", "/"))

def analyze(filename):
    print("Analyzing", filename)
    a, d, dx = androguard.misc.AnalyzeAPK(filename)

    if not (a and d and dx):
        print("Could not analyze..")
        return

    try:
        epclass = a.get_file("assets/xposed_init")
        epclass = epclass.decode("utf-8").split()[0]
    except FileNotPresent as e:
        print("File has no Xposed entrypoint")
        return

    print("Xposed entrypoint:", epclass)

    cls_analysis = dx.get_class_analysis(to_dalvik_notation(epclass))

    mca = dx.get_method_analysis_by_name(cls_analysis.get_vm_class().get_name(),
                                         "handleLoadPackage",
                                         "(Lde/robv/android/xposed/callbacks/XC_LoadPackage$LoadPackageParam;)V")
    ma = dx.get_method(mca.get_method())

    dec = androguard.decompiler.dad.decompile.DvMethod(ma)
    dec.process()

    IPython.embed()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: {0} <path_to.[dex|apk]>".format(sys.argv[0]))
        sys.exit(1)

    analyze(sys.argv[1])
