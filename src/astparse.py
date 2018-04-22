from enum import Enum

class ClassInstanceCreation:
    def __init__(self, node):
        assert(node[0] == "ClassInstanceCreation")
        self.type = parse_expression(node[2])
    def __str__(self):
        return "new ({0})".format(self.type)

class Literal:
    def __init__(self, node):
        assert(node[0] == "Literal")
        self.value = parse_expression(node[1])
    @classmethod
    def fromprimitive(cls, value):
        return cls(["Literal", str(value)])
    def __str__(self):
        return str(self.value)

class Local:
    def __init__(self, node):
        assert(node[0] == "Local")
        self.name = node[1]
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        return isinstance(other, Local) and self.name == other.name
    def __str__(self):
        return self.name

class TypeName:
    def __init__(self, node):
        assert(node[0] == "TypeName")
        self.name = node[1][0]
    def __str__(self):
        return "Type: " + self.name

class FieldAccess:
    def __init__(self, node):
        assert(node[0] == "FieldAccess")
        self.type = parse_expression(node[1][0])
        self.field = ".".join(x for x in node[2] if x)
    def __str__(self):
        return "Field: {0}".format(self.field)

class ArrayAccess:
    def __init__(self, node):
        assert(node[0] == "ArrayAccess")
        self.array = parse_expression(node[1][0])
        self.index = parse_expression(node[1][1])
    @classmethod
    def fromobj(cls, array, index):
        return cls(["ArrayAccess", [array, index]])
    def __hash__(self):
        return hash(self.array) + hash(self.index)
    def __eq__(self, other):
        return isinstance(other, ArrayAccess) and \
            self.array == other.array and self.index == other.index
    def __str__(self):
        return "{0}[{1}]".format(self.array, self.index)

class ArrayCreation:
    def __init__(self, node):
        assert(node[0] == "ArrayCreation")
        self.type = parse_expression(node[1][0])
        self.param = parse_expression(node[1][1])
    def __str__(self):
        return "new {0}[{1}]".format(self.type, self.param)

class Parameter:
    def __init__(self, node):
        self.type = parse_expression(node[0])
        self.name = parse_expression(node[1])
    def __str__(self):
        return "Param: {0} {1}".format(self.type, self.name)

class Assignment:
    def __init__(self, node):
        assert(node[0] == "Assignment")
        self.lhs = parse_expression(node[1][0])
        self.rhs = parse_expression(node[1][1])

    def __hash__(self):
        return hash(self.lhs)

    def __eq__(self, other):
        return isinstance(other, Assignment) and \
            other.lhs == self.lhs and other.rhs == self.rhs

    def __str__(self):
        return "{0} := {1}".format(self.lhs, self.rhs)

class LocalDeclarationStatement:
    def __init__(self, node):
        assert(node[0] == "LocalDeclarationStatement")
        self.value = parse_expression(node[1])
        self.type = parse_expression(node[2][0])
        self.name = parse_expression(node[2][1])
    def __str__(self):
        return "{0} {1} := {2}".format(self.type, self.name, self.value)

class MethodInvocation:
    def __init__(self, node):
        assert(node[0] == "MethodInvocation")
        self.base = parse_expression(node[1][0]) if node[4] else None
        self.params = [parse_expression(x) for x in node[1][(1 if self.base else 0):]]
        self.triple = node[2]
        self.name = node[3]

    def __str__(self):
        return "Invocation: {0}.{1}({2})".format(self.base, self.name, ",".join(str(x) for x in self.params))

def parse_expression(node):
    """
    Returns an instance representing the current 'node' object from
    the AST. If there is no appropriate class, the node itself is returned.
    """

    if type(node) == list:
        if node[0] == "ArrayAccess":
            return ArrayAccess(node)
        elif node[0] == "ArrayCreation":
            return ArrayCreation(node)
        elif node[0] == "ClassInstanceCreation":
            return ClassInstanceCreation(node)
        elif node[0] == "Literal":
            return Literal(node)
        elif node[0] == "FieldAccess":
            return FieldAccess(node)
        elif node[0] == "Local":
            return Local(node)
        elif node[0] == "TypeName":
            return TypeName(node)
        elif node[0] == "MethodInvocation":
            return MethodInvocation(node)
    return node


def dfs(graph, callback):

    """
    Perform a deph-first-search (DFS) on a 'graph' object

    Calls 'callback(node)' function for every node
    If callback returns False, the algorithm won't dive deeper
    into the current node.
    """
    stack = [x for x in reversed(graph)]
    while stack:
        node = stack.pop()
        if type(node) is list and len(node) > 0:
            # if callback returns False, don't go deeper
            if callback(node):
                stack.extend(reversed(node))
