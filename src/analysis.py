import pickle


class Hook:
    def __init__(self, classname, method, callbackobj):
        self.classname = classname
        self.method = method
        self.callbackobj = callbackobj

    def __str__(self):
        return "Hook {0}#{1}, callback object {2}".format(self.classname, self.method, self.callbackobj)

    def __repr__(self):
        return str(self.__dict__)


class Report:
    def __init__(self, name, file, hooks):
        self.name = name
        self.file = file
        self.hooks = hooks

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, "rb") as f:
            return pickle.load(f)
