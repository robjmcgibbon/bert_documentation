#! /usr/bin/python3

import subprocess
import os


def clone_swift(swift_directory, branch="master", source_url=None, source_path=None):

    if (source_url is None) and (source_path is None):
        print("Error: need to specify either source_url or source_path!")
        exit(1)
    if (not source_url is None) and (not source_path is None):
        print("Error: cannot specify both source_url or source_path!")
        exit(1)

    if os.path.exists("swift_directory"):
        print('Error: directory "{0}" already exists!'.format(swift_directory))
        exit(1)

    if (not source_path is None) and (not branch == "master"):
        print("Error: cannot change branches in a source folder copy!")
        exit(1)

    os.makedirs(swift_directory)

    if source_path is None:
        # need to clone the repository
        cmd = "git clone {0} .".format(source_url)
        df = subprocess.Popen(cmd, shell=True, cwd=swift_directory)
        df.wait()
        if df.returncode != 0:
            print("Error cloning repository!")
            exit(1)
    else:
        # need to copy over the repository from the source location
        cmd = "rsync -rvhtlP {0}/* .".format(source_path)
        df = subprocess.Popen(cmd, shell=True, cwd=swift_directory)
        df.wait()
        if df.returncode != 0:
            print("Error copying repository!")
            exit(1)

    if not branch == "master":
        cmd = "git checkout {0}".format(branch)
        df = subprocess.Popen(cmd, shell=True, cwd=swift_directory)
        df.wait()
        if df.returncode != 0:
            print("Error switching to branch {0}!".format(branch))
            exit(1)

    cmd = "./autogen.sh"
    df = subprocess.Popen(cmd, shell=True, cwd=swift_directory)
    df.wait()
    if df.returncode != 0:
        print("Error generating Automake files!")
        exit(1)


if __name__ == "__main__":

    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--url", "-u", action="store", default=None)
    argparser.add_argument("--path", "-p", action="store", default=None)
    argparser.add_argument("--branch", "-b", action="store", default="master")
    argparser.add_argument("directory", action="store")
    args = argparser.parse_args()

    clone_swift(args.directory, args.branch, args.url, args.path)
