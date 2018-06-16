def to_dv_notation(classname):
    return "L{0};".format(classname.replace(".", "/"))

def to_java_notation(classname):
    cn = classname[1:-1] if classname[0] == "L" and classname[-1] == ";" else classname
    return cn.replace("/", ".")