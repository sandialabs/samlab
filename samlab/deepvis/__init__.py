# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import collections
import functools
import logging
import math
import os
import shutil

import PIL.Image
import enlighten
import jinja2
import torch.nn
import torchvision.transforms.v2.functional

log = logging.getLogger(__name__)


def generate(*, modelname, model, targetdir, device=None, clean=True, batchsize=64, datasets=None, activations=True, html=True, seed=1234, examples=100):
    log.info(f"Generating deep visualization of {modelname} in {targetdir}")

    if datasets is None:
        datasets = []

    if device is None:
        device = torch.device("cpu")

    if clean and os.path.exists(targetdir):
        shutil.rmtree(targetdir)

    if not os.path.exists(targetdir):
        os.makedirs(targetdir)

    # Record channel activations.
    activations = {}

    model.to(device)

    def hook_fn(dataname, layername, module, inputs, outputs):
        if outputs.ndim == 2:
            activations[dataname][layername].append(outputs.detach().cpu())
        elif outputs.ndim == 4:
            activations[dataname][layername].append(torch.amax(outputs, dim=(2, 3)).detach().cpu())

    manager = enlighten.get_manager()
    for dataset in datasets:
        log.info(f"Generating activations for dataset {dataset['name']}.")

        activations[dataset["slug"]] = collections.defaultdict(list)

        handles = []
        for layername, module in model.named_modules():
            if not layername:
                continue

            if isinstance(module, torch.nn.Sequential):
                continue

            handles.append(module.register_forward_hook(functools.partial(hook_fn, dataset["slug"], layername)))

        counter = manager.counter(total=math.ceil(len(dataset["evaluate"]) / batchsize), desc="Activations", unit="batches", leave=False)
        loader = torch.utils.data.DataLoader(dataset["evaluate"], batch_size=batchsize, shuffle=False)
        for x, y in loader:
            y_hat = model(x.to(device))
            counter.update()
        counter.close()

        for handle in handles:
            handle.remove()

    for dataset in activations:
        activations[dataset] = {layer: torch.cat(activations[dataset][layer]) for layer in activations[dataset]}


    # Generate a context version of the model for page generation.
    contextmodel = []
    for name, module in model.named_modules():
        if not name:
            continue

        if isinstance(module, torch.nn.Sequential):
            continue

        layer = {
            "name": name,
            "slug": name,
            "type": str(module.__class__).split(".")[-1].split("'")[0],
            "channels": [],
            "conv": None,
        }

        if isinstance(module, torch.nn.Conv2d):
            size = module.get_parameter("weight").size()
            layer["channels"] = [{"name": f"{channel}"} for channel in range(size[0])]
            layer["conv"] = (int(size[2]), int(size[3]))
        elif isinstance(module, torch.nn.Linear):
            size = module.get_parameter("weight").size()
            layer["channels"] = [{"name": f"{channel}"} for channel in range(size[0])]

        for index, channel in enumerate(layer["channels"]):
            channel["slug"] = channel["name"]

            channel["examples"] = []
            for dataset in activations:
                layeract = activations[dataset][layer["slug"]]
                channelact = layeract.T[index]
                images = torch.argsort(channelact, descending=True)[:examples]
                acts = channelact[images]
                channel["examples"].append({
                    "dataset": dataset,
                    "images": images.tolist(),
                    "activations": acts.tolist(),
                })

        contextmodel.append(layer)

    # Generate HTML
    if html:
        # Copy assets to the target dir.
        log.info(f"Copying assets to {targetdir}")
        shutil.copytree(os.path.join(__path__[0], "templates", "css"), os.path.join(targetdir, "css"), dirs_exist_ok=True)
        shutil.copytree(os.path.join(__path__[0], "templates", "js"), os.path.join(targetdir, "js"), dirs_exist_ok=True)

        # Setup the context and environment for generating pages.
        context = {
            "webroot": "/",
            "datasets": datasets,
            "modelname": modelname,
            "model": contextmodel,
        }

        environment = jinja2.Environment(
            loader=jinja2.PackageLoader("samlab.deepvis"),
            autoescape=jinja2.select_autoescape(),
            )

        # Generate the home page.
        log.info(f"Generating home page.")
        with open(os.path.join(targetdir, "index.html"), "w") as stream:
            stream.write(environment.get_template("index.html").render(context))

        # Generate per-layer pages.
        for layer in contextmodel:
            log.info(f"Generating layer {layer['name']}.")
            context["layer"] = layer

            layerdir = os.path.join(targetdir, "layers", layer["name"])
            if not os.path.exists(layerdir):
                os.makedirs(layerdir)

            with open(os.path.join(layerdir, "index.html"), "w") as stream:
                stream.write(environment.get_template("layer.html").render(context))

            # Generate per-channel pages.
            counter = manager.counter(total=len(layer["channels"]), desc="Channels", unit="channels", leave=False)
            for channel in layer["channels"]:
                context["channel"] = channel

                channeldir = os.path.join(layerdir, "channels", channel["name"])
                if not os.path.exists(channeldir):
                    os.makedirs(channeldir)

                    with open(os.path.join(channeldir, "index.html"), "w") as stream:
                        stream.write(environment.get_template("channel.html").render(context))
                counter.update()
            counter.close()

        # Generate per-dataset pages.
        for dataset in datasets:
            log.info(f"Generating dataset {dataset['name']}.")
            context["dataset"] = dataset

            datasetdir = os.path.join(targetdir, "datasets", dataset["slug"])
            if not os.path.exists(datasetdir):
                os.makedirs(datasetdir)

            with open(os.path.join(datasetdir, "index.html"), "w") as stream:
                stream.write(environment.get_template("dataset.html").render(context))

            # Generate disk images.
            imagedir = os.path.join(datasetdir, "images")
            if not os.path.exists(imagedir):
                os.makedirs(imagedir)

            counter = manager.counter(total=len(dataset["view"]), desc="Images", unit="images", leave=False)
            for index in range(len(dataset["view"])):
                imagepath = os.path.join(imagedir, f"image-{index}.png")
                if not os.path.exists(imagepath):
                    sample = dataset["view"][index]
                    sample[0].save(imagepath)
                counter.update()
            counter.close()

