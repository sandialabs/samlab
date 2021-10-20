# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import glob
import os
import shutil
import subprocess

for path in glob.glob(".coverage*"):
    os.remove(path)
if os.path.exists(".cover"):
    shutil.rmtree(".cover")
subprocess.call(["coverage", "run", "--parallel-mode", "--source", "samlab", "-m", "behave"])
subprocess.call(["coverage", "combine"])
subprocess.call(["coverage", "report"])
subprocess.call(["coverage", "html", "--directory", ".cover"])
