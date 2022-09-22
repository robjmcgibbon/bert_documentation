import argparse
import os
import shutil


def create_directory(name, copylist, linklist, force=True):
    if os.path.exists(name):
        if force:
            shutil.rmtree(name)
        else:
            raise RuntimeError(f"Directory {name} already exists!")
    os.makedirs(name)

    for cfilepath in copylist:
        _, cfile = os.path.split(cfilepath)
        shutil.copy(cfilepath, f"{wdir}/{cfile}")
    for lfilepath in linklist:
        _, lfile = os.path.split(lfilepath)
        os.symlink(lfilepath, f"{wdir}/{lfile}")


def parse_file_list(filename):
    files = []
    with open(filename, "r") as handle:
        for line in handle.readlines():
            commpos = line.find("#")
            if commpos != -1:
                line = line[:commpos]
            line = line.strip()
            if line != "":
                files.append(os.path.abspath(line))
    return files


if __name__ == "__main__":

    argparser = argparse.ArgumentParser(
        "Set up a simulation directory."
        " Also copy over files in the provided copy file."
        " Also creates soft links to the files in the provided link file."
    )
    argparser.add_argument("directory", help="Name of the directory to create.")
    argparser.add_argument(
        "--copy", "-c", default=None, help="List of files that should be copied over."
    )
    argparser.add_argument(
        "--link",
        "-l",
        default=None,
        help="List of files to which a soft link should be created.",
    )
    argparser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Overwrite the directory if it already exists.",
        default=False,
    )
    args = argparser.parse_args()

    copylist = []
    if args.copy is not None:
        copylist = parse_file_list(args.copy)

    linklist = []
    if args.link is not None:
        linklist = parse_file_list(args.link)

    print(copylist, linklist)
    exit()

    create_directory(args.directory, copylist, linklist, args.force)
