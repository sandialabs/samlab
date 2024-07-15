# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Provides a command line interface for generating visualizations.
"""

import argparse
import logging
import os
import sys

import samlab
import samlab.deepvis

# Setup the command line user interface.
parser = argparse.ArgumentParser(description="SAMLAB tools.")
subparsers = parser.add_subparsers(title="commands (choose one)", dest="command")

# deepvis
deepvis_subparser = subparsers.add_parser("deepvis", help="Generate a deep visualization website.")
deepvis_subparser.add_argument("--output", "-o", help="Directory to receive results. Default: cwd")

# version
version_subparser = subparsers.add_parser("version", help="Print the Samlab version.")


def main():
    arguments = parser.parse_args()

    if arguments.command is None:
        parser.print_help()

    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger()
    log.name = os.path.basename(sys.argv[0])

    # deepvis
    if arguments.command == "deepvis":
        samlab.deepvis.generate(None, arguments.output)

    # version
    if arguments.command == "version":
        print(samlab.__version__)


