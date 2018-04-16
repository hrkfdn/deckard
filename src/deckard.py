#!/usr/bin/env python3

import IPython

import sys
import json
import androguard.misc

import astparse

def get_pkg_names(ast):
    pkgnames = set()
    invocations = traverseAST(ast)

    strcomps = [x for x in invocations
                if x.triple == ('java/lang/String', 'equals', '(Ljava/lang/Object;)Z')]
    for c in strcomps:
        litval, ispkgcheck = None, None
        for p in c.params:
            if p.ptype == ParameterType.LITERAL:
                litval = p.value
            elif p.ptype == ParameterType.FIELD and \
                 p.triple == ('de/robv/android/xposed/callbacks/XC_LoadPackage$LoadPackageParam',\
                              'packageName', 'Ljava/lang/String;'):
                ispkgcheck = True
        if litval and ispkgcheck:
            pkgnames.add(litval)
    return list(pkgnames)

def to_dalvik_notation(name):
    return "L{0};".format(name.replace(".", "/"))

def analyze_method(method):
    invocations = []
    assignments = {}

    def dfs_callback(node):
        if node[0] == "MethodInvocation":
            invocations.append(astparse.MethodInvocation(node))
            return False
        elif node[0] == "Assignment":
            print(node)
            assignment = astparse.Assignment(node)
            print("lhs:", assignment.lhs)
            print("rhs:", assignment.rhs)
            assignments[assignment.lhs] = assignment

        return True

    decompiler = androguard.decompiler.dad.decompile.DvMethod(method)
    decompiler.process(doAST=True)
    ast = decompiler.ast

    astparse.dfs(ast['body'], dfs_callback)

    print("Function calls in", method)
    for i in invocations:
        print(i)
        print("\tParameters")
        for p in i.params:
            print("\t\t", p)

def analyze(filename):
    print("Analyzing", filename)
    a, d, dx = androguard.misc.AnalyzeAPK(filename)

    if not (a and d and dx):
        print("Could not analyze..")
        return

    cls = dx.get_class_analysis("Lde/robv/android/xposed/XposedHelpers;")
    if not cls:
        print("No reference to Xposed found. Is this an Xposed module?")
        return

    clsparam = dx.get_method_analysis_by_name(cls.get_vm_class().get_name(),
                                              "findAndHookMethod",
                                              "(Ljava/lang/Class; Ljava/lang/String; [Ljava/lang/Object;)Lde/robv/android/xposed/XC_MethodHook$Unhook;")
    strparam = dx.get_method_analysis_by_name(cls.get_vm_class().get_name(),
                                              "findAndHookMethod",
                                              "(Ljava/lang/String; Ljava/lang/ClassLoader; Ljava/lang/String; [Ljava/lang/Object;)Lde/robv/android/xposed/XC_MethodHook$Unhook;")
    if not (clsparam or strparam):
        print("No references to findAndHookMethod() found")
        return

    # gather all methods referencing findAndHookMethod() and store them in a set
    methods = set()
    xrefs = []
    if strparam: xrefs.extend(strparam.get_xref_from())
    if clsparam: xrefs.extend(clsparam.get_xref_from())

    for xref in xrefs:
        (xref_class, xref_method, xref_offset) = xref
        methods.add(dx.get_method(xref_method))

    for m in methods:
        analyze_method(m)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: {0} <path_to.[dex|apk]>".format(sys.argv[0]))
        sys.exit(1)

    analyze(sys.argv[1])
