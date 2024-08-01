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


class TransformedDataset(torch.utils.data.Dataset):
    def __init__(self, dataset, transform):
        self._dataset = dataset
        self._transform = transform

    def __len__(self):
        return self._dataset.__len__()

    def __getitem__(self, key):
        item = self._dataset.__getitem__(key)
        item = (self._transform(item[0]), item[1])
        return item


def createcontext(*, batchsize, datasets, device, examples, model, title, webroot):
    # Create the global context.
    context = Namespace(
        datasets=datasets,
        model=Namespace(layers=[]),
        title=title,
        url=webroot,
        webroot=webroot,
    )

    # Expand the dataset model.
    for dataset in context.datasets:
        dataset.url = f"{webroot}datasets/{dataset.slug}"
        dataset.samples = []

        categories = set()
        for index in range(len(dataset.view)):
            image, category = dataset.view[index]
            categories.add(category)

            dataset.samples.append(Namespace(
                activations=[],
                category=category,
                imageurl=f"{webroot}datasets/{dataset.slug}/samples/{index}/image.png",
                index=index,
                url=f"{webroot}datasets/{dataset.slug}/samples/{index}",
                ))
        dataset.categories = [Namespace(name=category) for category in categories]

    # Create the layer model.
    for name, module in model.named_modules():
        if not name:
            continue

        if isinstance(module, torch.nn.Sequential):
            continue

        layer = Namespace(
            channels=[],
            conv=None,
            module=module,
            name=name,
            type=str(module.__class__).split(".")[-1].split("'")[0],
        )

        if isinstance(module, torch.nn.Conv2d):
            size = module.get_parameter("weight").size()
            layer.channels = [Namespace(index=index) for index in range(size[0])]
            layer.conv = (int(size[2]), int(size[3]))
        elif isinstance(module, torch.nn.Linear):
            size = module.get_parameter("weight").size()
            layer.channels = [Namespace(index=index) for index in range(size[0])]

        context.model.layers.append(layer)

    # Expand the layer model.
    for index, layer in enumerate(context.model.layers):
        layer.activations = []
        layer.index = index
        layer.url=f"{webroot}layers/{index}"

    # Expand the channel model.
    for layer in context.model.layers:
        for channel in layer.channels:
            channel.url = f"{webroot}layers/{layer.index}/channels/{channel.index}"

    # Compute activations.
    model.to(device)

    def hook_fn(layer, module, inputs, outputs):
        if outputs.ndim == 2:
            layer.activations[-1].values.append(outputs.detach().cpu())
        elif outputs.ndim == 4:
            layer.activations[-1].values.append(torch.amax(outputs, dim=(2, 3)).detach().cpu())

    for dataset in context.datasets:
        log.info(f"Generating activations for dataset {dataset.name}")

        handles = []
        for layer in context.model.layers:
            layer.activations.append(Namespace(dataset=dataset, values=[]))
            handles.append(layer.module.register_forward_hook(functools.partial(hook_fn, layer)))

        counter = enlighten.get_manager().counter(total=math.ceil(len(dataset.evaluate) / batchsize), desc="Activations", unit="batches", leave=False)
        loader = torch.utils.data.DataLoader(dataset.evaluate, batch_size=batchsize, shuffle=False)
        for x, y in loader:
            y_hat = model(x.to(device))
            counter.update()
        counter.close()

        for handle in handles:
            handle.remove()

        for layer in context.model.layers:
            layer.activations[-1].values = torch.cat(layer.activations[-1].values)

    # Assign activations to channels.
    for layer in context.model.layers:
        for channel in layer.channels:
            channel.activations = []
            for activations in layer.activations:
                values = activations.values.T[channel.index]
                samples = torch.argsort(values, descending=True)[:examples]
                channel.activations.append(Namespace(
                    dataset=activations.dataset,
                    samples=[activations.dataset.samples[index] for index in samples],
                    values=values[samples].tolist(),
                ))

    # Assign activations to dataset samples.
    for layer in context.model.layers:
        if not len(layer.channels):
            continue
        for activations in layer.activations:
            for sample, values in zip(activations.dataset.samples, activations.values):
                channels = torch.argsort(values, descending=True)[:10]
                sample.activations.append(Namespace(
                    layer=layer,
                    channels=[layer.channels[index] for index in channels],
                    values = values[channels].tolist(),
                    ))

    return context


def generate(*,
    batchsize,
    clean,
    datasets,
    device,
    examples,
    model,
    targetdir,
    title,
    webroot,
    ):
    log.info(f"Generating deep visualization {title} in {targetdir}.")

    # Create the object model that will be used by Jinja templates.
    context = createcontext(batchsize=batchsize, datasets=datasets, device=device, examples=examples, model=model, title=title, webroot=webroot)

    # Optionally remove the target directory.
    if clean and os.path.exists(targetdir):
        log.info(f"Removing {targetdir}")
        shutil.rmtree(targetdir)

    # Create the target directory.
    log.info(f"Creating {targetdir}")
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)

    # Copy assets to the target directory.
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
        counter = enlighten.get_manager().counter(total=len(layer.channels), desc="Channels", unit="channels", leave=False)
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
        counter = enlighten.get_manager().counter(total=len(dataset.samples), desc="Samples", unit="samples", leave=False)
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

