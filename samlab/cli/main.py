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
deepvis_subparser.add_argument("--clean", action="store_true", help="Delete the target directory before generating.")
deepvis_subparser.add_argument("--device", default="cpu", help="PyTorch device to use for evaluation. Default: %(default)s")
deepvis_subparser.add_argument("--examples", type=int, default=100, help="Number of examples to display for each channel. Default: %(default)s")
deepvis_subparser.add_argument("--imagenet", help="Specify the path to the ImageNet 2012 classification dataset, and use it for testing.")
deepvis_subparser.add_argument("--imagenet-count", type=int, help="Number of ImageNet 2012 images to use for testing. Default: all")
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
            case "resnet50":
                title = "ResNet-50"
                model = torchvision.models.resnet50(weights="IMAGENET1K_V2")
            case "inceptionv1":
                title = "Inception v1"
                model = torchvision.models.googlenet(weights="IMAGENET1K_V1")
            case _:
                raise NotImplementedError(f"Unsupported model: {arguments.model}")

        datasets = []

        # Optionally use ImageNet for testing.
        if arguments.imagenet is not None:
            evaluate = torchvision.datasets.ImageNet(
                arguments.imagenet,
                transform=torchvision.transforms.v2.Compose([
                    torchvision.transforms.v2.ToImage(),
                    torchvision.transforms.v2.CenterCrop((224, 224)),
                    torchvision.transforms.v2.ToDtype(torch.float32, scale=True),
                    torchvision.transforms.v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                    lambda x: (x,),
                    ]),
                )

            classes = evaluate.classes

            view = torchvision.datasets.ImageNet(
                arguments.imagenet,
                transform=torchvision.transforms.v2.Compose([
                    torchvision.transforms.v2.CenterCrop((224, 224)),
                    lambda x: (x,),
                    ]),
                target_transform=lambda y: f"{classes[y][0]} ({y})",
                )


            if arguments.imagenet_count is not None:
                weights = torch.ones(len(view))
                indices = torch.sort(torch.multinomial(weights, arguments.imagenet_count, generator=generator))[0]
                evaluate = torch.utils.data.Subset(evaluate, indices)
                view = torch.utils.data.Subset(view, indices)

            datasets.append(samlab.deepvis.Namespace(
                name="ImageNet 2012",
                slug="imagenet2012",
                evaluate=evaluate,
                view=view,
                ))

        # Generate the website.
        samlab.deepvis.generate(
            batchsize=arguments.batch_size,
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


