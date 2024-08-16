# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import glob
import os
import shutil
import subprocess
import sys

for path in glob.glob(".coverage*"):
    if path not in [".coveragerc"]:
        os.remove(path)
if os.path.exists(".cover"):
    shutil.rmtree(".cover")
subprocess.call(["coverage", "run", "-m", "behave"] + sys.argv[1:])
subprocess.call(["coverage", "combine"])
subprocess.call(["coverage", "report"])
subprocess.call(["coverage", "html", "--directory", ".cover"])
