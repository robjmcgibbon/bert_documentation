#!/usr/bin/env python3

import subprocess
import sys
import os


def get_environment_for_modules(modules, module_path = None):
    python = sys.executable

    module_cmd = "module_purge\n"
    if module_path is not None:
      module_cmd += f"module use {module_path}\n"
    module_cmd += f"module load {' '.join(modules)}\n"

    cmd = f'echo "{module_cmd} {python} {os.path.dirname(__file__)}/dump_environment.py" | /bin/bash'

    stdout = open("/usr/tmp/dump_environment.out", "w")
    stderr = open("/usr/tmp/dump_environment.err", "w")

    df = subprocess.Popen(cmd, shell=True, stdout=stdout, stderr=stderr)
    df.wait()
    stdout.close()
    stderr.close()

    if df.returncode != 0:
        print("Error retrieving module environment:")
        print(open("/usr/tmp/dump_environment.err", "r").read())
        exit(1)

    stdout = open("/usr/tmp/dump_environment.out", "r").read()

    env = {}
    for row in stdout.split("\n"):
        if len(row) > 0:
            cols = row.split("\t")
            if len(cols) == 2:
                env[cols[0]] = cols[1]

    return env


if __name__ == "__main__":

    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("modules", action="store", nargs="+")
    args = argparser.parse_args()

    print(get_environment_for_modules(args.modules))
