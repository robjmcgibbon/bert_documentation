#!/usr/bin/env python3

import os
import pickle
import sys

env = os.environ.copy()

for key in env:
    if not "BASH" in key:
        sys.stdout.write("{0}\t{1}\n".format(key, env[key]))
