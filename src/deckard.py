#!/usr/bin/env python3

from pathlib import Path
import sys

import analysis
import static


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: {0} <path_to.[dex|apk]>".format(sys.argv[0]))
        sys.exit(1)

    reportpath = Path(sys.path[0]).parent / "reports"

    target = Path(sys.argv[1])
    if not target.exists():
        print("File {0} does not exist".format(target))
        sys.exit(1)

    hooks = static.analyze(sys.argv[1])
    report = analysis.Report(target.name, hooks)

    report.save(reportpath / (target.name + ".report"))
