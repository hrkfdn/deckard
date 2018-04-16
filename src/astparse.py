from enum import Enum

class Literal:
    def __init__(self, node):
        self.value = parse_expression(node[1])
    def __str__(self):
        return "Literal: " + str(self.value)

class Identifier:
    def __init__(self, node):
        self.name = node[1]
    def __str__(self):
        return "Local: " + self.name

class TypeName:
    def __init__(self, node):
        assert(node[0] == "TypeName")
        self.name = node[1][0]

class FieldAccess:
    def __init__(self, node):
        assert(node[0] == "FieldAccess")
        self.field = parse_expression(node[1])

class ArrayAccess:
    def __init__(self, node):
        assert(node[0] == "ArrayAccess")
        self.array = parse_expression(node[1])

def parse_expression(node):
    if type(node) == list:
        if node[0] == "ArrayAccess":
            return ArrayAccess(node)
        elif node[0] == "Literal":
            return Literal(node)
        elif node[0] == "FieldAccess":
            return FieldAccess(node)
        elif node[0] == "Local":
            return Identifier(node)
        elif node[0] == "TypeName":
            return TypeName(node)
        elif node[0] == "MethodInvocation":
            return MethodInvocation(node)
    return node

class Assignment:
    def __init__(self, data):
        print("Assignment()", data)
        self.lhs = parse_expression(data[1][0])
        self.rhs = parse_expression(data[1][1])
        print(self.lhs, "=", self.rhs)

    def __hash__(self):
        return hash(self.lhs)

    def __eq__(self, other):
        return isinstance(Assignment) and \
            other.lhs == self.lhs and other.rhs == self.rhs

class MethodInvocation:
    def __init__(self, data):
        assert(data[0] == "MethodInvocation")
        self.params = [parse_expression(x) for x in data[1]]
        self.triple = data[2]
        self.name = data[3]
        self.base = data[4]

    def __str__(self):
        return "Invocation: " + str(self.triple)

def dfs(graph, callback):
    stack = [x for x in reversed(graph)]
    while stack:
        node = stack.pop()
        if type(node) is list and len(node) > 0:
            # if callback returns False, don't go deeper
            if callback(node):
                stack.extend(reversed(node))
