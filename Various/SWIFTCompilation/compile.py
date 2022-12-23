#! /usr/bin/python3

import get_module_environment
import subprocess


def compile_swift(swift_directory, modules, configuration=None, threads=16):

    # modules simply set some environment variables (e.g. PATH)
    # by copying this environment into a dict, we can reuse it for configuration
    # and compilation without having to load modules explicitly
    # (which would not work with subprocess anyway)
    env = get_module_environment.get_environment_for_modules(modules)

    if not configuration is None:
        cmd = "./configure {0}".format(" ".join(configuration))
        df = subprocess.Popen(cmd, shell=True, env=env, cwd=swift_directory)
        df.wait()
        if df.returncode != 0:
            print("Configuration error!")
            exit(1)

    df = subprocess.Popen(
        "make -j {0}".format(threads), shell=True, env=env, cwd=swift_directory
    )
    df.wait()
    if df.returncode != 0:
        print("Compilation error!")
        exit(1)


if __name__ == "__main__":

    import argparse
    import os

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--reconfigure", "-c", action="store_true")
    argparser.add_argument("--threads", "-j", action="store", type=int, default=16)
    argparser.add_argument(
        "--working-directory", "-d", action="store", default=os.getcwd()
    )
    args = argparser.parse_args()

    modules = ["OpenMPI"]

    config = None
    if args.reconfigure:
        config = [
            "--with-subgrid=COLIBRE",
            "--enable-task-debugging",
            "--enable-threadpool-debugging",
            "--enable-cell-graph",
            "--enable-debugging-checks",
        ]

    compile_swift(args.working_directory, modules, config, args.threads)
