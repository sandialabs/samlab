# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import os
import pkgutil
import re
import subprocess
import sys

from behave import *
import nose.tools

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


@given(u'all Samlab sources.')
def step_impl(context):
    context.sources = []
    for directory, subdirectories, filenames in os.walk(root_dir):
        for filename in filenames:
            extension = os.path.splitext(filename)[1]
            if extension == ".js":
                if "samlab" not in filename:
                    continue
            elif extension == ".py":
                pass
            else:
                continue
            context.sources.append(os.path.join(directory, filename))
    context.sources = sorted(context.sources)


@then(u'every Python source must contain a copyright notice.')
def step_impl(context):
    copyright_notice = """# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""
    missing = []
    for source in context.sources:
        if os.path.splitext(source)[1] not in [".py"]:
            continue
        with open(source, "r") as stream:
            if not stream.read().startswith(copyright_notice):
                missing.append(source)
    if missing:
        raise AssertionError("Missing copyright notices:\n\n%s" % "\n".join(missing))


@then(u'every Javascript source must contain a copyright notice.')
def step_impl(context):
    copyright_notice = """// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

"""
    missing = []
    for source in context.sources:
        if os.path.splitext(source)[1] not in [".js"]:
            continue
        if re.search("[.]cover/", source):
            continue
        if re.search("docs/_build/html", source):
            continue
        if os.path.basename(source) in [
                "bootstrap.bundle.min.js",
                "bootstrap-notify.min.js",
                "css.min.js",
                "element-resize-event.js",
                "IPv6.js",
                "jquery.gridster.js",
                "jquery.min.js",
                "jquery-ui.min.js",
                "knockout.mapping.min.js",
                "knockout-min.js",
                "knockout-projections.js",
                "lodash.min.js",
                "mousetrap.min.js",
                "OBJLoader.js",
                "OrbitControls.js",
                "punycode.js",
                "require.min.js",
                "SecondLevelDomains.js",
                "URI.js",
                "socket.io.slim.js",
                "text.min.js",
                "three.js",
            ]:
            continue
        with open(source, "r") as stream:
            if not stream.read().startswith(copyright_notice):
                missing.append(source)
    if missing:
        raise AssertionError("Missing copyright notices:\n\n%s" % "\n".join(missing))

