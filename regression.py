# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import argparse
import subprocess

parser = argparse.ArgumentParser("Run all Samlab regression tests.")
arguments = parser.parse_args()

subprocess.run(["coverage", "run", "--source", "samlab", "-m", "behave", "--tags", "~@wip"])
subprocess.run(["coverage", "combine"])
subprocess.run(["coverage", "report"])
subprocess.run(["coverage", "html", "--directory", ".cover"])


