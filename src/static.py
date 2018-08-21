import androguard.misc
import androguard.decompiler.dad.decompile
import re

import analysis
import astparse
import utils


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
        if not type(inv.base) is astparse.TypeName:
            continue
        if (inv.base.name == "de/robv/android/xposed/XposedHelpers" and \
            (inv.name == "findAndHookMethod" or \
             inv.name == "findAndHookConstructor")) or \
            (inv.base.name == "de/robv/android/xposed/XposedBridge" and \
             (inv.name == "hookAllConstructors")):

            if type(resolve_identifier(ctx, inv.params[-1])) is astparse.Parameter:
                hook_obj = resolve_identifier(ctx, inv.params[-1])
            elif type(inv.params[-1]) is not astparse.ClassInstanceCreation:
                # hook objects are passed as an Object array of N elements.
                # where N-1 elements are the classes of the target function's parameters
                # and the last/N-th element contains the XC_MethodHook instance, which
                # we are trying to extract.
                hook_array = inv.params[-1]
                hook_array_size = ctx[str(hook_array)].param.value
                hook_obj_identifier = "{0}[{1}]".format(hook_array, int(hook_array_size) - 1)
                hook_obj = resolve_identifier(ctx, hook_obj_identifier)
            else:
                # hookAllConstructors receives a direct XC_MethodHook instance
                hook_obj = inv.params[-1]

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
                cls = cls.name.replace("/", ".")

            targetmethod = resolve_identifier(ctx, inv.params[-2]) if inv.name == "findAndHookMethod" else None

            # we can't deal with dynamic class names in static analysis
            if type(cls) is not str:
                print("Target class ({0}) is dynamic, skipping hook {0}#{1}".format(cls, targetmethod))
                continue

            # also skip dynamic method names
            if not type(targetmethod) in [str, type(None)]:
                print("Target method ({0}) is dynamic, skipping hook {0}#{1}".format(cls, targetmethod))
                continue

            # and dynamic hook objects
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


def analyze(a, d, dx):
    if not (a and d and dx):
        print("Could not analyze..")
        return []

    xh = dx.get_class_analysis("Lde/robv/android/xposed/XposedHelpers;")
    if not xh:
        print("No reference to Xposed found. Is this an Xposed module?")
        return []

    m_clsparam = dx.get_method_analysis_by_name(xh.get_vm_class().get_name(),
                                                "findAndHookMethod",
                                                "(Ljava/lang/Class; Ljava/lang/String; "
                                                "[Ljava/lang/Object;)Lde/robv/android/xposed/XC_MethodHook$Unhook;")
    m_strparam = dx.get_method_analysis_by_name(xh.get_vm_class().get_name(),
                                                "findAndHookMethod",
                                                "(Ljava/lang/String; Ljava/lang/ClassLoader; Ljava/lang/String; "
                                                "[Ljava/lang/Object;)Lde/robv/android/xposed/XC_MethodHook$Unhook;")
    c_clsparam = dx.get_method_analysis_by_name(xh.get_vm_class().get_name(),
                                                "findAndHookConstructor",
                                                "(Ljava/lang/Class; [Ljava/lang/Object;)Lde/robv/android/xposed"
                                                "/XC_MethodHook$Unhook;")
    c_strparam = dx.get_method_analysis_by_name(xh.get_vm_class().get_name(),
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

def analyze_callback(a, d, dx, callback):
    result = []
    decompiler = androguard.decompiler.dad.decompile.DvMethod(dx.get_method(callback.get_method()))
    decompiler.process(doAST=True)
    ast = decompiler.ast
    context = {}

    for p in ast["params"]:
        param = astparse.Parameter(p)
        context[str(param.name)] = param

    invocations = []
    def dfs_callback(node):
        parsed = astparse.parse_expression(node)
        if type(parsed) is not list:
            print("callback:", parsed)
        if node[0] == "MethodInvocation":
            invocations.append((parsed, context.copy()))
        if node[0] == "LocalDeclarationStatement":
            context[str(parsed.name)] = parsed.value
        elif node[0] == "Assignment":
            context[str(parsed.lhs)] = parsed.rhs
        return True

    astparse.dfs(ast['body'], dfs_callback)

    for inv, ctx in invocations:
        if inv.name == "setResult" and inv.triple[0] == "de/robv/android/xposed/XC_MethodHook$MethodHookParam":
            result.append("Setting return value to " + str(inv.params[0]))
        elif inv.triple[0] == "de/robv/android/xposed/XposedHelpers":
            rex = re.match(r"set(.*)Field", inv.name)
            if rex:
                result.append("Setting {0} of {1} to {2}".format(rex[1],
                                                                 resolve_identifier(ctx, inv.params[1]),
                                                                 resolve_identifier(ctx, inv.params[2])))
            rex = re.match(r"get(.*)Field", inv.name)
            if rex:
                result.append("Getting {0} field \"{1}\" of {2}".format(rex[1],
                                                                        resolve_identifier(ctx, inv.params[1]),
                                                                        resolve_identifier(ctx, inv.params[0])))
            rex = re.match(r"call(.*)Method", inv.name)
            if rex:
                result.append("Calling {0} method \"{2}\" of {1}".format(rex[1],
                                                                         resolve_identifier(ctx, inv.params[0]),
                                                                         resolve_identifier(ctx, inv.params[1])))

    return result

def analyze_hooks(a, d, dx, hook):
    result = {}
    cbname = hook.callbackobj.replace("$", "\$")  # $ needs to be escaped as callgraph generator expects regexps

    for cb in dx.find_methods(utils.to_dv_notation(cbname),
                              "^(after|before)HookedMethod$",
                              "\(Lde/robv/android/xposed/XC_MethodHook\$MethodHookParam;\)V"):
        name = cb.get_method().get_name()
        analysis = analyze_callback(a, d, dx, cb)
        if analysis:
            result[name] = analysis

    return result
