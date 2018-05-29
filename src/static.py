import androguard.misc
import androguard.decompiler.dad.decompile

import analysis
import astparse


def resolve_identifier(context, identifier):
    """
    Recursively resolves identifiers defined in 'context'
    """
    start = identifier
    while str(start) in context:
        start = context.get(str(start))
    if type(start) is astparse.Literal:
        start = start.value
    return start


def analyze_method(method):
    """
    Analyze Androguard MethodAnalysis object in 'method' for Xposed hooks
    """
    hooks = []
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
        context[str(param.name)] = param

    astparse.dfs(ast['body'], dfs_callback)

    for inv, ctx in invocations:
        if type(inv.base) is astparse.TypeName and \
                inv.base.name == "de/robv/android/xposed/XposedHelpers" and \
                (inv.name == "findAndHookMethod" or inv.name == "findAndHookConstructor"):
            # hook objects are passed as an Object array of N elements.
            # where N-1 elements are the classes of the target function's parameters
            # and the last/N-th element contains the XC_MethodHook instance, which
            # we are trying to extract.
            hook_array = inv.params[-1]
            hook_array_size = ctx[str(hook_array)].param.value
            hook_obj_identifier = "{0}[{1}]".format(hook_array, int(hook_array_size) - 1)
            hook_obj = resolve_identifier(ctx, hook_obj_identifier)

            # get hook class if referenced directly in a class instance creation
            if isinstance(hook_obj, astparse.ClassInstanceCreation):
                hook_obj = hook_obj.type

            # extract class names from calls to XposedHelpers.findClass(className, classLoader)
            # a pattern common in Xposed module hooks
            cls = resolve_identifier(ctx, inv.params[0])
            if isinstance(cls, astparse.MethodInvocation) and isinstance(cls.base, astparse.TypeName):
                if cls.base.name == "de/robv/android/xposed/XposedHelpers" and cls.name == "findClass":
                    # resolve parameter once more in case a local/variable was passed
                    cls = resolve_identifier(ctx, cls.params[0])
            # class literals
            elif isinstance(cls, astparse.TypeName):
                cls = cls.name

            targetmethod = resolve_identifier(ctx, inv.params[-2]) if inv.name == "findAndHookMethod" else None
            if type(hook_obj) is not astparse.TypeName:
                print("Callback object ({0}) is dynamic, skipping hook {1}#{2}".format(hook_obj, cls, targetmethod))
                continue

            callback = hook_obj.name

            hook = analysis.Hook(cls, targetmethod, callback)

            hooks.append(hook)
            # print("Context:")
            # for k, v in ctx.items():
            #    print("\t", k, "=", v)
    return hooks


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

    m_clsparam = dx.get_method_analysis_by_name(cls.get_vm_class().get_name(),
                                                "findAndHookMethod",
                                                "(Ljava/lang/Class; Ljava/lang/String; "
                                                "[Ljava/lang/Object;)Lde/robv/android/xposed/XC_MethodHook$Unhook;")
    m_strparam = dx.get_method_analysis_by_name(cls.get_vm_class().get_name(),
                                                "findAndHookMethod",
                                                "(Ljava/lang/String; Ljava/lang/ClassLoader; Ljava/lang/String; "
                                                "[Ljava/lang/Object;)Lde/robv/android/xposed/XC_MethodHook$Unhook;")
    c_clsparam = dx.get_method_analysis_by_name(cls.get_vm_class().get_name(),
                                                "findAndHookConstructor",
                                                "(Ljava/lang/Class; [Ljava/lang/Object;)Lde/robv/android/xposed"
                                                "/XC_MethodHook$Unhook;")
    c_strparam = dx.get_method_analysis_by_name(cls.get_vm_class().get_name(),
                                                "findAndHookConstructor",
                                                "(Ljava/lang/String; Ljava/lang/ClassLoader; "
                                                "[Ljava/lang/Object;)Lde/robv/android/xposed/XC_MethodHook$Unhook;")

    if not (m_clsparam or m_strparam):
        print("No references to findAndHookMethod() found")
    if not (c_clsparam or c_strparam):
        print("No references to findAndHookConstructor() found")

    # gather all methods referencing findAndHookMethod() and store them in a set
    methods = set()
    xrefs = []
    for x in [m_strparam, m_clsparam, c_strparam, c_clsparam]:
        if x:
            xrefs.extend(x.get_xref_from())

    for xref in xrefs:
        (xref_class, xref_method, xref_offset) = xref
        methods.add(dx.get_method(xref_method))

    hooks = []
    for m in methods:
        hooks.extend(analyze_method(m))

    return hooks
