#!/usr/bin/env python3

import sys

import static


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: {0} <path_to.[dex|apk]>".format(sys.argv[0]))
        sys.exit(1)

    static.analyze(sys.argv[1])
