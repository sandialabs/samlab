# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging
import os
import shutil

import jinja2

log = logging.getLogger(__name__)


def generate(modelname, model, targetdir, clean=True):
    log.info(f"Generating deep visualization of {modelname} in {targetdir}")

    if clean and os.path.exists(targetdir):
        shutil.rmtree(targetdir)

    if not os.path.exists(targetdir):
        os.makedirs(targetdir)

    # Copy assets to the target dir.
    shutil.copytree(os.path.join(__path__[0], "templates", "css"), os.path.join(targetdir, "css"))
    shutil.copytree(os.path.join(__path__[0], "templates", "js"), os.path.join(targetdir, "js"))

    # Generate the home page.
    environment = jinja2.Environment(
        loader=jinja2.PackageLoader("samlab.deepvis"),
        autoescape=jinja2.select_autoescape(),
        )

    context = {
        "webroot": "/",
        "modelname": modelname,
        "model": [{"name": name, "type": repr(type(module))} for name, module in model.named_modules()],
    }

    with open(os.path.join(targetdir, "index.html"), "w") as stream:
        stream.write(environment.get_template("index.html").render(context))

    # Generate layer pages.
    layerdir = os.path.join(targetdir, "layer")
    if not os.path.exists(layerdir):
        os.makedirs(layerdir)

    for name, module in model.named_modules():
        context["layername"] = name

        with open(os.path.join(targetdir, "layer", f"{name}.html"), "w") as stream:
            stream.write(environment.get_template("layer.html").render(context))

