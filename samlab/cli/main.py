# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Provides a command line interface for generating visualizations.
"""

import argparse
import logging
import os
import sys

import torch.utils.data
import torchvision.datasets
import torchvision.models

import samlab
import samlab.deepvis


# Setup the command line user interface.
parser = argparse.ArgumentParser(description="SAMLAB tools.")
subparsers = parser.add_subparsers(title="commands (choose one)", dest="command")

# deepvis
deepvis_subparser = subparsers.add_parser("deepvis", help="Generate a deep visualization website.")
deepvis_subparser.add_argument("--clean", action="store_true", help="Delete the target directory before generating.")
deepvis_subparser.add_argument("--imagenet", help="Specify the path to the ImageNet 2012 classification dataset, and use it for testing.")
deepvis_subparser.add_argument("--imagenet-count", type=int, help="Number of ImageNet 2012 images to use for testing. Default: all")
deepvis_subparser.add_argument("model", choices=["vgg19", "resnet50", "inceptionv1"], help="Model to analyze.")
deepvis_subparser.add_argument("output", help="Target directory to receive results.")

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
                modelname = "VGG-19"
                model = torchvision.models.vgg19(weights="IMAGENET1K_V1")
            case "resnet50":
                modelname = "ResNet-50"
                model = torchvision.models.resnet50(weights="IMAGENET1K_V2")
            case "inceptionv1":
                modelname = "Inception v1"
                model = torchvision.models.googlenet(weights="IMAGENET1K_V1")
            case _:
                raise NotImplementedError(f"Unsupported model: {arguments.model}")

        datasets = []
        if arguments.imagenet is not None:
            dataset = torchvision.datasets.ImageNet(arguments.imagenet)
            if arguments.imagenet_count is not None:
                dataset = torch.utils.data.Subset(dataset, indices)
            datasets.append({"name": "ImageNet 2012", "dataset": dataset})

        samlab.deepvis.generate(
            modelname=modelname,
            model=model,
            targetdir=arguments.output,
            clean=arguments.clean,
            datasets=datasets,
            )

    # version
    if arguments.command == "version":
        print(samlab.__version__)


