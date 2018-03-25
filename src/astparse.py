from enum import Enum

class ParameterType(Enum):
    OTHER = 0
    LITERAL = 1
    FIELD = 2

class Parameter:
    def __init__(self, data):
        self.ptype = ParameterType.OTHER
        self.value = data[1]
        self.literaltype = None
        self.triple = None

        if data[0] == "Literal":
            self.ptype = ParameterType.LITERAL
            self.literaltype = data[2]
        elif data[0] == "FieldAccess":
            self.ptype = ParameterType.FIELD
            self.triple = data[2]
        else:
            self.ptype = ParameterType.OTHER

    def __str__(self):
        return "Parameter: {0} ({1}) [{2} {3}]".format(self.value,
                                                       self.triple,
                                                       self.ptype,
                                                       self.literaltype)

class Invocation:
    def __init__(self, data):
        if data[0] != "MethodInvocation":
            raise ValueError("Supplied data is no MethodInvocation object")

        self.params = [Parameter(x) for x in data[1]]
        self.triple = data[2]
        self.name = data[3]
        self.base = data[4]

    def __str__(self):
        return "Invocation: " + str(self.triple)

def get_invocations(graph):
    invocations = []
    stack = [x for x in graph]
    while stack:
        vertex = stack.pop()
        if type(vertex) is list and len(vertex) > 0:
            if vertex[0] == "MethodInvocation":
                invocations.append(Invocation(vertex))
            else:
                stack.extend(vertex)
    return invocations

def traverseAST(ast):
    # handleLoadPackage method signature is predefined, grab parameter
    # variable name so we can identify it in the AST
    firstparam = ast['params'][0]
    for node in firstparam:
        if node[0] == "TypeName" and \
           "de/robv/android/xposed/callbacks/XC_LoadPackage$LoadPackageParam" not in node[1]:
            print("First parameter is not of type LoadPackageParam, aborting")
            sys.exit(1)
        if node[0] == "Local":
            paramvar = node[1]

    #print("LoadPackageParam is named", paramvar)

    return get_invocations(ast['body'])
