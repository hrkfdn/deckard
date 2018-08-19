import fileinput
import os
import sys

import analysis
import utils


def is_deckard_line(line):
    return len(line) == 8 and line[5] == "Deckard"

def parse_lines(lines):
    hooks = set()

    for line in [l.split() for l in lines]:
        if is_deckard_line(line):
            entries = line[7].split("|")
            if len(entries) == 4:
                src, targetclass, targetmethod, hookobj = entries[0], entries[1], entries[2], entries[3]
                hooks.add(analysis.Hook(targetclass, targetmethod, hookobj))

    return hooks

def get_input(progname, apk):
    is_pipe = not os.isatty(sys.stdin.fileno())

    if not is_pipe:
        print("Please use ADB to pipe the device's logcat to Deckard to generate a dynamic analysis report")
        print("Example:")
        print("$ adb logcat \"Deckard:V *:S\" | {0} dynamic {1}".format(progname, apk))
        sys.exit(1)

    print("Waiting for input on stdin. Use CTRL-C to finish capture.")

    # stdin reading loop
    buf = ""
    lines = []
    try:
        while True:
            buf += sys.stdin.read(1)
            if len(buf) and buf[-1] == "\n":
                line = buf.strip()
                if is_deckard_line(line.split()):
                    print("XPOSED HOOK:", line)
                    lines.append(line)
                else:
                    print("INFO:", line)
                buf = ""
    except KeyboardInterrupt:
        return lines

def filter(hooks, dx):
    filtered = []

    for hook in hooks:
        if dx.get_class_analysis(utils.to_dv_notation(hook.callbackobj)):
            filtered.append(hook)
        else:
            print("Discarding hook not originating from this module:", hook.callbackobj)

    return filtered
