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
import torchvision.transforms.v2

import samlab
import samlab.deepvis


# Setup the command line user interface.
parser = argparse.ArgumentParser(description="SAMLAB tools.")
subparsers = parser.add_subparsers(title="commands (choose one)", dest="command")

# deepvis
deepvis_subparser = subparsers.add_parser("deepvis", help="Generate a deep visualization website.")
deepvis_subparser.add_argument("--batch-size", type=int, default=64, help="Batch size for evaluation. Default: %(default)s")
deepvis_subparser.add_argument("--caltech", action="store_true", help="Use Caltech 101 for testing.")
deepvis_subparser.add_argument("--caltech-count", type=int, help="Number of Caltech 101 images to use for testing. Default: all")
deepvis_subparser.add_argument("--caltech-path", help="Specify the path to the Caltech 101 classification dataset.")
deepvis_subparser.add_argument("--clean", action="store_true", help="Delete the target directory before generating.")
deepvis_subparser.add_argument("--device", default="cpu", help="PyTorch device to use for evaluation. Default: %(default)s")
deepvis_subparser.add_argument("--examples", type=int, default=100, help="Number of examples to display for each channel. Default: %(default)s")
deepvis_subparser.add_argument("--imagenet", action="store_true", help="Use ImageNet 2012 for testing.")
deepvis_subparser.add_argument("--imagenet-count", type=int, help="Number of ImageNet 2012 images to use for testing. Default: all")
deepvis_subparser.add_argument("--imagenet-path", help="Specify the path to the ImageNet 2012 classification dataset.")
deepvis_subparser.add_argument("--places", action="store_true", help="Use Places365 for testing.")
deepvis_subparser.add_argument("--places-count", type=int, help="Number of Places365 images to use for testing. Default: all")
deepvis_subparser.add_argument("--places-path", help="Specify the path to the Places365 classification dataset.")
deepvis_subparser.add_argument("--seed", type=int, default=1234, help="Random seed. Default: %(default)s")
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

    generator = torch.Generator()
    generator.manual_seed(arguments.seed)

    # deepvis
    if arguments.command == "deepvis":
        match arguments.model:
            case "vgg19":
                title = "VGG-19"
                model = torchvision.models.vgg19(weights="IMAGENET1K_V1")
                imagenet = torchvision.datasets.ImageNet(arguments.imagenet_path)
                channelnames = {"classifier.6": [classes[0] for classes in imagenet.classes]}
            case "resnet50":
                title = "ResNet-50"
                model = torchvision.models.resnet50(weights="IMAGENET1K_V2")
                channelnames = {}
            case "inceptionv1":
                title = "Inception v1"
                model = torchvision.models.googlenet(weights="IMAGENET1K_V1")
                channelnames = {}
            case _:
                raise NotImplementedError(f"Unsupported model: {arguments.model}")

        datasets = []

        # Optionally use Caltech 101 for testing.
        if arguments.caltech:
            datasets.append(samlab.deepvis.caltech101(arguments.caltech_path, arguments.caltech_count, generator))


        # Optionally use ImageNet for testing.
        if arguments.imagenet:
            datasets.append(samlab.deepvis.imagenet2012(arguments.imagenet_path, arguments.imagenet_count, generator))

        # Optionally use Places365 for testing.
        if arguments.places:
            datasets.append(samlab.deepvis.places365(arguments.places_path, arguments.places_count, generator))

        # Generate the website.
        samlab.deepvis.generate(
            batchsize=arguments.batch_size,
            channelnames=channelnames,
            clean=arguments.clean,
            datasets=datasets,
            device=torch.device(arguments.device),
            examples=arguments.examples,
            model=model,
            targetdir=arguments.output,
            title=title,
            webroot="/",
            )

    # version
    if arguments.command == "version":
        print(samlab.__version__)


