import json

class Hook:
    def __init__(self, classname, method, callbackobj):
        self.classname = classname
        self.method = method
        self.callbackobj = callbackobj

    def __str__(self):
        return "Hook {0}#{1}, callback object {2}".format(self.classname, self.method, self.callbackobj)