# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import collections
import functools
import logging
import math
import os
import shutil
import types

import PIL.Image
import enlighten
import jinja2
import torch.nn
import torchvision.transforms.v2.functional

log = logging.getLogger(__name__)


class Namespace(types.SimpleNamespace):
    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)

    def keys(self):
        return self.__dict__.keys()

    def __getitem__(self, key):
        return self.__dict__[key]


def createcontext(*, activations, datasets, examples, model, title, webroot):
    context = Namespace(
        datasets=datasets,
        model=Namespace(layers=[]),
        title=title,
        webroot=webroot,
#        examplecount=examples,
    )

    # Add dataset samples.
    for dataset in context.datasets:
        dataset.samples = [Namespace(index=index) for index in range(len(dataset.view))]

    # Add layer data.
    layerindex = 0
    for name, module in model.named_modules():
        if not name:
            continue

        if isinstance(module, torch.nn.Sequential):
            continue

        layer = Namespace(
            name=name,
            index=layerindex,
            type=str(module.__class__).split(".")[-1].split("'")[0],
            channels=[],
            conv=None,
        )

        if isinstance(module, torch.nn.Conv2d):
            size = module.get_parameter("weight").size()
            layer.channels = [Namespace(index=index) for index in range(size[0])]
            layer.conv = (int(size[2]), int(size[3]))
        elif isinstance(module, torch.nn.Linear):
            size = module.get_parameter("weight").size()
            layer.channels = [Namespace(index=index) for index in range(size[0])]

        for channel in layer.channels:
            channel.examples = []
            for dataset in activations:
                layeract = activations[dataset][layer.name]
                channelact = layeract.T[channel.index]
                images = torch.argsort(channelact, descending=True)[:examples]
                acts = channelact[images]
                channel.examples.append(Namespace(
                    dataset=dataset,
                    images=images.tolist(),
                    activations=acts.tolist(),
                ))

        context.model.layers.append(layer)
        layerindex += 1

    return context


def generate(*,
    activations,
    batchsize,
    clean,
    datasets,
    device,
    examples,
    html,
    model,
    seed,
    targetdir,
    title,
    webroot,
    ):

    log.info(f"Generating deep visualization of {title} in {targetdir}")

    if clean and os.path.exists(targetdir):
        log.info(f"Cleaning {targetdir}")
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
        log.info(f"Generating activations for dataset {dataset.name}")

        activations[dataset.slug] = collections.defaultdict(list)

        handles = []
        for layername, module in model.named_modules():
            if not layername:
                continue

            if isinstance(module, torch.nn.Sequential):
                continue

            handles.append(module.register_forward_hook(functools.partial(hook_fn, dataset.slug, layername)))

        counter = manager.counter(total=math.ceil(len(dataset.evaluate) / batchsize), desc="Activations", unit="batches", leave=False)
        loader = torch.utils.data.DataLoader(dataset.evaluate, batch_size=batchsize, shuffle=False)
        for x, y in loader:
            y_hat = model(x.to(device))
            counter.update()
        counter.close()

        for handle in handles:
            handle.remove()

    for dataset in activations:
        activations[dataset] = {layer: torch.cat(activations[dataset][layer]) for layer in activations[dataset]}


    # Generate HTML
    if html:
        context = createcontext(activations=activations, datasets=datasets, examples=examples, model=model, title=title, webroot=webroot)

        # Copy assets to the target dir.
        log.info(f"Copying assets to {targetdir}")
        shutil.copytree(os.path.join(__path__[0], "templates", "css"), os.path.join(targetdir, "css"), dirs_exist_ok=True)
        shutil.copytree(os.path.join(__path__[0], "templates", "js"), os.path.join(targetdir, "js"), dirs_exist_ok=True)

        environment = jinja2.Environment(
            loader=jinja2.PackageLoader("samlab.deepvis"),
            autoescape=jinja2.select_autoescape(),
            )

        # Generate the home page.
        log.info(f"Generating home page.")
        with open(os.path.join(targetdir, "index.html"), "w") as stream:
            stream.write(environment.get_template("index.html").render(context))

        # Generate per-layer pages.
        for layer in context.model.layers:
            log.info(f"Generating layer {layer.name}")
            context.layer = layer

            layerdir = os.path.join(targetdir, "layers", str(layer.index))
            if not os.path.exists(layerdir):
                os.makedirs(layerdir)

            with open(os.path.join(layerdir, "index.html"), "w") as stream:
                stream.write(environment.get_template("layer.html").render(context))

            # Generate per-channel pages.
            counter = manager.counter(total=len(layer.channels), desc="Channels", unit="channels", leave=False)
            for channel in layer.channels:
                context.channel = channel

                channeldir = os.path.join(layerdir, "channels", str(channel.index))
                if not os.path.exists(channeldir):
                    os.makedirs(channeldir)

                with open(os.path.join(channeldir, "index.html"), "w") as stream:
                    stream.write(environment.get_template("channel.html").render(context))

                counter.update()
            counter.close()

        # Generate per-dataset pages.
        for dataset in context.datasets:
            log.info(f"Generating dataset {dataset.name}.")
            context.dataset = dataset

            datasetdir = os.path.join(targetdir, "datasets", dataset.slug)
            if not os.path.exists(datasetdir):
                os.makedirs(datasetdir)

            with open(os.path.join(datasetdir, "index.html"), "w") as stream:
                stream.write(environment.get_template("dataset.html").render(context))

            # Generate per-sample pages.
            counter = manager.counter(total=len(dataset.samples), desc="Samples", unit="samples", leave=False)
            for sample in dataset.samples:
                context.sample = sample

                sampledir = os.path.join(datasetdir, "samples", f"{sample.index}")
                if not os.path.exists(sampledir):
                    os.makedirs(sampledir)

                with open(os.path.join(sampledir, "index.html"), "w") as stream:
                    stream.write(environment.get_template("sample.html").render(context))

                imagepath = os.path.join(sampledir, f"image.png")
                dataset.view[sample.index][0].save(imagepath)
                counter.update()
            counter.close()

