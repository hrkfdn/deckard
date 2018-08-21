#!/usr/bin/env python3

from pathlib import Path
import sys

from androguard import misc
from androguard import session

import analysis
import dynamic
import static
import webui

def save_report(hooks, reportpath, target):
    if len(hooks) == 0:
        print("No hooks identified. Not saving report.")
    else:
        print("{0} hook(s) identified, generating report".format(len(hooks)))
        report = analysis.Report(target.name, hooks, (a, d, dx))
        report.save(reportpath / (target.name + ".report"))
        print("Report saved to", reportpath / (target.name + ".report"))

if __name__ == "__main__":
    sys.setrecursionlimit(50000)

    if len(sys.argv) < 3:
        print("usage: {0} <static|dynamic|show> <path_to.apk|path_to.report>".format(sys.argv[0]))
        sys.exit(1)

    reportpath = Path(sys.path[0]).parent / "reports"

    target = Path(sys.argv[2])
    if not target.exists():
        print("File {0} does not exist".format(target))
        sys.exit(1)

    if sys.argv[1] == "static":
        filebuf = None
        with open(target, "rb") as f:
            filebuf = f.read()

        if filebuf:
            a, d, dx = misc.AnalyzeAPK(filebuf, raw=True)
            hooks = set(static.analyze(a, d, dx))
            save_report(hooks, reportpath, target)
    elif sys.argv[1] == "dynamic":
        lines = dynamic.get_input(sys.argv[0], target)
        hooks = set(dynamic.parse_lines(lines))
        print("{} hooks captured".format(len(hooks)))
        a, d, dx = misc.AnalyzeAPK(target)
        hooks_filtered = set(dynamic.filter(hooks, dx))
        save_report(hooks_filtered, reportpath, target)

    elif sys.argv[1] == "show":
        report = analysis.Report.load(target)
        webui.serve(report)
