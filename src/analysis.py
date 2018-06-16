import hashlib
import pickle
import pygments
import pygments.lexers

import utils


class Hook:
    def __init__(self, classname, method, callbackobj):
        assert(type(classname) is str)
        assert(type(method) in [str, type(None)])  # method can be None for constructor hooks
        assert(type(callbackobj) is str)

        self.classname = classname
        self.method = method
        self.callbackobj = callbackobj

    def calchash(self):
        md5 = hashlib.md5()
        md5.update(self.classname.encode("utf-8"))
        if self.method:
            md5.update(self.method.encode("utf-8"))
        md5.update(self.callbackobj.encode("utf-8"))
        return md5.hexdigest()

    @property
    def isconstructor(self):
        return self.method is None

    @property
    def human_name(self):
        if self.isconstructor:
            return self.classname
        else:
            return "{0}.{1}".format(self.classname, self.method)

    def __str__(self):
        return "Hook {0}#{1}, callback object {2}".format(self.classname, self.method, self.callbackobj)

    def __repr__(self):
        return str(self.__dict__)


class Report:
    def __init__(self, name, hooks, session):
        self.name = name
        self.hooks = {x.calchash(): x for x in hooks}
        self.session = session

    def get_source(self, hook, highlight=True):
        (a, d, dx) = self.session
        ca = dx.get_class_analysis(utils.to_dv_notation(hook.callbackobj))
        src = ca.get_vm_class().get_source()

        if highlight:
            return pygments.highlight(src, pygments.lexers.JavaLexer(), pygments.formatters.HtmlFormatter())
        else:
            return src

    def get_cg(self, hook):
        def get_vis_nodes(nodes, idprefix=""):
            return [{"id": idprefix + str(n),
                     "label": "{0}\n{1}".format(utils.to_java_notation(n.class_name).split(".")[-1], n.name),
                     "color": "#ffb3b3" if n.name.endswith("HookedMethod") else "#b3c6ff" }
                    for n in nodes]
        def get_vis_edges(edges, idprefix=""):
            return [{"from": idprefix + str(e[0]),
                     "to": idprefix + str(e[1])}
                    for e in set(edges)]

        (a, d, dx) = self.session
        cbname = hook.callbackobj.replace("$", "\$")  # $ needs to be escaped as callgraph generator expects regexps

        cg_before = dx.get_call_graph(classname=utils.to_dv_notation(cbname), methodname="beforeHookedMethod")
        cg_after = dx.get_call_graph(classname=utils.to_dv_notation(cbname), methodname="afterHookedMethod")

        nodes = get_vis_nodes(cg_before.nodes) + get_vis_nodes(cg_after.nodes, "+")
        edges = get_vis_edges(cg_before.edges) + get_vis_edges(cg_after.edges, "+")

        return {"nodes": nodes, "edges": edges}

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, "rb") as f:
            return pickle.load(f)
