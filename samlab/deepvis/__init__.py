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


def createcontext(*, batchsize, channelnames, datasets, device, examples, model, title, webroot):
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
        log.info(f"Scanning dataset {dataset.name}")
        dataset.samples = []
        dataset.url = f"{webroot}datasets/{dataset.slug}"

        categories = set()
        counter = enlighten.get_manager().counter(total=len(dataset.view), desc="Scan", unit="samples", leave=False)
        for index in range(len(dataset.view)):
            x, y = dataset.view[index]
            categories.add(y)

            dataset.samples.append(Namespace(
                activations=[],
                category=Namespace(index=y[0], name=y[1]),
                imageurl=f"{webroot}datasets/{dataset.slug}/samples/{index}/image.png",
                index=index,
                name=f"Sample {index}",
                url=f"{webroot}datasets/{dataset.slug}/samples/{index}",
                ))
            counter.update()
        dataset.categories = [Namespace(index=index, name=name) for index, name in categories]
        counter.close()

    # Create the layer model.
    for name, module in model.named_modules():
        if not name:
            continue

        if isinstance(module, torch.nn.Sequential):
            continue

        index = len(context.model.layers)

        layer = Namespace(
            activations=[],
            channels=[],
            conv=None,
            index=index,
            module=module,
            name=name,
            nchannels=0,
            type=str(module.__class__).split(".")[-1].split("'")[0],
            url=f"{webroot}layers/{index}",
        )

        if isinstance(module, torch.nn.Conv2d):
            layer.conv = tuple(module.get_parameter("weight").size()[2:4])

        context.model.layers.append(layer)

    # Add layer navigation fields.
    for layer in context.model.layers:
        layer.nexturl=f"{webroot}layers/{(layer.index+1) % len(context.model.layers)}"
        layer.prevurl=f"{webroot}layers/{(layer.index-1) % len(context.model.layers)}"

    # Compute activations.
    model.to(device)

    def hook_fn(layer, module, inputs, outputs):
        layer.nchannels = outputs.shape[1]
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

        counter = enlighten.get_manager().counter(total=math.ceil(len(dataset.evaluate) / batchsize), desc="Evaluate", unit="batches", leave=False)
        loader = torch.utils.data.DataLoader(dataset.evaluate, batch_size=batchsize, shuffle=False)
        for x, y in loader:
            x = (item.to(device) for item in x)
            y_hat = model(*x)
            counter.update()
        counter.close()

        for handle in handles:
            handle.remove()

        for layer in context.model.layers:
            layer.activations[-1].values = torch.cat(layer.activations[-1].values)

    # Create the channel model.
    for layer in context.model.layers:
        for index in range(layer.nchannels):
            layer.channels.append(Namespace(
                index=index,
                name=channelnames[layer.name][index] if layer.name in channelnames else f"Channel {index}",
                url=f"{webroot}layers/{layer.index}/channels/{index}",
                nexturl=f"{webroot}layers/{layer.index}/channels/{(index+1) % layer.nchannels}",
                prevurl = f"{webroot}layers/{layer.index}/channels/{(index-1) % layer.nchannels}",
                ))

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
    channelnames,
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
    context = createcontext(batchsize=batchsize, channelnames=channelnames, datasets=datasets, device=device, examples=examples, model=model, title=title, webroot=webroot)

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
        counter = enlighten.get_manager().counter(total=len(layer.channels), desc="Generate", unit="channels", leave=False)
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
        counter = enlighten.get_manager().counter(total=len(dataset.samples), desc="Generate", unit="samples", leave=False)
        for sample in dataset.samples:
            context.sample = sample

            sampledir = os.path.join(datasetdir, "samples", f"{sample.index}")
            if not os.path.exists(sampledir):
                os.makedirs(sampledir)

            with open(os.path.join(sampledir, "index.html"), "w") as stream:
                stream.write(environment.get_template("sample.html").render(context))

            imagepath = os.path.join(sampledir, f"image.png")
            x, y = dataset.view[sample.index]
            x[0].save(imagepath)
            counter.update()
        counter.close()


def imagenet2012(path, count, generator):
    evaluate = torchvision.datasets.ImageNet(
        path,
        transform=torchvision.transforms.v2.Compose([
            torchvision.transforms.v2.ToImage(),
            torchvision.transforms.v2.CenterCrop((224, 224)),
            torchvision.transforms.v2.ToDtype(torch.float32, scale=True),
            torchvision.transforms.v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            lambda x: (x,),
            ]),
        )

    dictionary = [item[0] for item in evaluate.classes]

    view = torchvision.datasets.ImageNet(
        path,
        transform=torchvision.transforms.v2.Compose([
            torchvision.transforms.v2.CenterCrop((224, 224)),
            lambda x: (x,),
            ]),
        target_transform=map_classes(dictionary),
        )


    if count is not None:
        weights = torch.ones(len(view))
        indices = torch.sort(torch.multinomial(weights, count, generator=generator))[0]
        evaluate = torch.utils.data.Subset(evaluate, indices)
        view = torch.utils.data.Subset(view, indices)

    return Namespace(
        name="ImageNet 2012",
        slug="imagenet2012",
        evaluate=evaluate,
        view=view,
        )


def map_classes(dictionary):
    def implementation(index):
        return (index, dictionary[index])
    return implementation


def places365(path, count, generator):
    evaluate = torchvision.datasets.Places365(
        path,
        transform=torchvision.transforms.v2.Compose([
            torchvision.transforms.v2.ToImage(),
            torchvision.transforms.v2.CenterCrop((224, 224)),
            torchvision.transforms.v2.ToDtype(torch.float32, scale=True),
            torchvision.transforms.v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            lambda x: (x,),
            ]),
        )

    dictionary = ["/".join(item.split("/")[2:]) for item in evaluate.classes]

    view = torchvision.datasets.Places365(
        path,
        transform=torchvision.transforms.v2.Compose([
            torchvision.transforms.v2.CenterCrop((224, 224)),
            lambda x: (x,),
            ]),
        target_transform=map_classes(dictionary),
        )


    if count is not None:
        weights = torch.ones(len(view))
        indices = torch.sort(torch.multinomial(weights, count, generator=generator))[0]
        evaluate = torch.utils.data.Subset(evaluate, indices)
        view = torch.utils.data.Subset(view, indices)

    return Namespace(
        name="Places",
        slug="places365",
        evaluate=evaluate,
        view=view,
        )


