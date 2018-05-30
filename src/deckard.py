#!/usr/bin/env python3

from pathlib import Path
import sys

from androguard import misc
from androguard import session

import analysis
import static
import webui


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
            hooks = static.analyze(a, d, dx)
            report = analysis.Report(target.name, hooks, (a, d, dx))
            report.save(reportpath / (target.name + ".report"))

    elif sys.argv[1] == "show":
        report = analysis.Report.load(target)
        webui.serve(report)