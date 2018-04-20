#!/usr/bin/env python3

import IPython

import sys
import json
import androguard.misc

import astparse

def resolve_identifier(context, identifier):
    """
    Recursively resolves identifiers defined in 'context'
    """
    start = identifier
    while str(start) in context:
        start = context.get(str(start))
    return start

def analyze_method(method):
    """
    Analyze Androguard MethodAnalysis object in 'method' for Xposed hooks
    """
    invocations = []
    context = {}

    def dfs_callback(node):
        if node[0] == "MethodInvocation":
            invocations.append((astparse.MethodInvocation(node), context))
            return False
        if node[0] == "LocalDeclarationStatement":
            decl = astparse.LocalDeclarationStatement(node)
            context[str(decl.name)] = decl.value
            return False
        elif node[0] == "Assignment":
            assignment = astparse.Assignment(node)
            context[str(assignment.lhs)] = assignment.rhs
            return False

        return True

    decompiler = androguard.decompiler.dad.decompile.DvMethod(method)
    decompiler.process(doAST=True)
    ast = decompiler.ast

    for p in ast["params"]:
        param = astparse.Parameter(p)
        context[param.name] = param

    astparse.dfs(ast['body'], dfs_callback)

    for inv, ctx in invocations:
        if type(inv.base) is astparse.TypeName and \
           inv.base.name == "de/robv/android/xposed/XposedHelpers" and \
           inv.name == "findAndHookMethod":
            # hook objects are passed as an Object array of N elements.
            # where N-1 elements are the classes of the target function's parameters
            # and the last/N-th element contains the XC_MethodHook instance, which
            # we are trying to extract.
            hook_array = inv.params[-1]
            hook_array_size = ctx[str(hook_array)].param.value
            hook_obj_identifier = "{0}[{1}]".format(hook_array, int(hook_array_size)-1)
            hook_obj = resolve_identifier(ctx, hook_obj_identifier)

            # get hook class if referenced directly in a class instance creation
            if isinstance(hook_obj, astparse.ClassInstanceCreation):
                hook_obj = hook_obj.type

            print("Hook information:")
            print("\tTarget class:", resolve_identifier(ctx, inv.params[0]))
            print("\tMethod name:", resolve_identifier(ctx, inv.params[-2]))
            print("\tHook object:", hook_obj)
            #print("Context:")
            #for k, v in ctx.items():
            #    print("\t", k, "=", v)

def analyze(filename):
    """
    Analyze an APK file located at 'filename'
    """
    print("Analyzing", filename)
    if filename.endswith(".dex"):
        a, d, dx = androguard.misc.AnalyzeDex(filename)
    else:
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
        print("Analyzing", m)
        analyze_method(m)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: {0} <path_to.[dex|apk]>".format(sys.argv[0]))
        sys.exit(1)

    analyze(sys.argv[1])
