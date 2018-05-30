import hashlib
import pickle


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

    def __str__(self):
        return "Hook {0}#{1}, callback object {2}".format(self.classname, self.method, self.callbackobj)

    def __repr__(self):
        return str(self.__dict__)


class Report:
    def __init__(self, name, hooks, session):
        self.name = name
        self.hooks = {x.calchash() : x for x in hooks}
        self.session = session

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, "rb") as f:
            return pickle.load(f)
