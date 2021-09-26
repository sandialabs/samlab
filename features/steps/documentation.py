# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import os
import pkgutil
import subprocess
import sys

from behave import *

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
docs_dir = os.path.join(root_dir, "docs")
python_docs_dir = os.path.join(docs_dir, "python")
javascript_docs_dir = os.path.join(docs_dir, "javascript")
package_dir = os.path.join(root_dir, "samlab")
javascript_module_dir = os.path.join(root_dir, "samlab", "web", "app", "static")


@given(u'all Python modules')
def step_impl(context):
    def walk_modules(package, path):
        modules = []
        modules.append(package)
        for loader, name, is_package in pkgutil.iter_modules([path]):
            modules += walk_modules(package + "." + name, os.path.join(path, name))
        return modules
    context.modules = sorted(walk_modules("samlab", package_dir))


@given(u'the Python reference documentation')
def step_impl(context):
    context.references = []
    for directory, subdirectories, filenames in os.walk(python_docs_dir):
        for filename in filenames:
            if os.path.splitext(filename)[1] not in [".rst"]:
                continue

            context.references.append(os.path.join(directory, filename))
    context.references = sorted(context.references)


@then(u'every Python module must have a section in the Python reference documentation')
def step_impl(context):
    missing = []
    for module in context.modules:
        if os.path.join(python_docs_dir, module + ".rst") not in context.references:
            missing.append(module)

    if missing:
        raise AssertionError("No matching documentation found for the following modules:\n\n%s" % "\n".join(missing))


@then(u'every section in the Python reference documentation must match a Python module')
def step_impl(context):
    missing = []
    modules = [os.path.join(python_docs_dir, module + ".rst") for module in context.modules]
    for reference in context.references:
        if reference not in modules:
            missing.append(reference)

    if missing:
        raise AssertionError("No matching module found for the following documentation:\n\n%s." % "\n".join(missing))


@given(u'all Javascript modules')
def step_impl(context):
    context.modules = []
    for directory, subdirectories, filenames in os.walk(javascript_module_dir):
        for filename in filenames:
            if os.path.splitext(filename)[1] not in [".js"]:
                continue
            if not filename.startswith("samlab"):
                continue

            context.modules.append(os.path.splitext(filename)[0])
    context.modules = sorted(context.modules)


@given(u'the Javascript reference documentation')
def step_impl(context):
    context.references = []
    for directory, subdirectories, filenames in os.walk(javascript_docs_dir):
        for filename in filenames:
            if os.path.splitext(filename)[1] not in [".rst"]:
                continue

            context.references.append(os.path.splitext(filename)[0])
    context.references = sorted(context.references)


@then(u'every Javascript module must have a section in the Javascript reference documentation')
def step_impl(context):
    missing = []
    for module in context.modules:
        if module not in context.references:
            missing.append(module)

    if missing:
        raise AssertionError("No matching documentation found for the following modules:\n\n%s" % "\n".join(missing))


@then(u'every section in the Javascript reference documentation must match a Javascript module')
def step_impl(context):
    missing = []
    for reference in context.references:
        if reference not in context.modules:
            missing.append(reference)

    if missing:
        raise AssertionError("No matching module found for the following documentation:\n\n%s." % "\n".join(missing))


