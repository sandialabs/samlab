# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import os
import pkgutil
import re
import subprocess
import sys

from behave import *

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


@given(u'all Samlab sources.')
def step_impl(context):
    context.sources = []
    for directory, subdirectories, filenames in os.walk(root_dir):
        for filename in filenames:
            extension = os.path.splitext(filename)[1]
            if extension == ".py":
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


