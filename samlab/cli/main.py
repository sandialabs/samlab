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

import torchvision.models


# Setup the command line user interface.
parser = argparse.ArgumentParser(description="SAMLAB tools.")
subparsers = parser.add_subparsers(title="commands (choose one)", dest="command")

# deepvis
deepvis_subparser = subparsers.add_parser("deepvis", help="Generate a deep visualization website.")
deepvis_subparser.add_argument("model", choices=["vgg19", "resnet50", "inceptionv1"], help="Model to analyze.")
deepvis_subparser.add_argument("output", help="Directory to receive results.")

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
        match arguments.model:
            case "vgg19":
                arguments.model = torchvision.models.vgg19(weights="IMAGENET1K_V1")
            case "resnet50":
                arguments.model = torchvision.models.resnet50(weights="IMAGENET1K_V2")
            case "inceptionv1":
                arguments.model = torchvision.models.googlenet(weights="IMAGENET1K_V1")
            case _:
                raise NotImplementedError(f"Unsupported model: {arguments.model}")

        samlab.deepvis.generate(arguments.model, arguments.output)

    # version
    if arguments.command == "version":
        print(samlab.__version__)


