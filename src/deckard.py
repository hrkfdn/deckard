#!/usr/bin/env python3

import IPython

import sys
import json
import androguard.misc

import astparse

def analyze_method(method):
    invocations = []
    context = {}

    def dfs_callback(node):
        if node[0] == "MethodInvocation":
            invocations.append((astparse.MethodInvocation(node), context))
            return False
        if node[0] == "LocalDeclarationStatement":
            decl = astparse.LocalDeclarationStatement(node)
            context[decl.name] = decl
        elif node[0] == "Assignment":
            assignment = astparse.Assignment(node)
            context[assignment.lhs] = assignment

        return True

    decompiler = androguard.decompiler.dad.decompile.DvMethod(method)
    decompiler.process(doAST=True)
    ast = decompiler.ast

    for p in ast["params"]:
        param = astparse.Parameter(p)
        context[param.name] = param

    astparse.dfs(ast['body'], dfs_callback)

    print("Function calls in", method)
    for i, a in invocations:
        print(i)
        print("\tParameters:")
        for p in i.params:
            print("\t\t", p)
        print("\tContext:")
        for k, v in a.items():
            print("\t\t", v)

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
