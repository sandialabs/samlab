# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.


# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
sys.path.insert(0, os.path.abspath(".."))


# -- Project information -----------------------------------------------------

project = "Samlab"
copyright = "2018, National Technology & Engineering Solutions of Sandia, LLC (NTESS)"
author = "Timothy M. Shead"

# The full version, including alpha/beta/rc tags
import samlab
release = samlab.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

import sphinx_rtd_theme

extensions = [
    "nbsphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_gallery.load_style",
    "sphinx_rtd_theme",
]


autodoc_mock_imports = [
"IPython",
"arrow",
"flask_socketio",
"ldap3",
"numpy",
"requests",
"scipy",
"torch",
"toyplot",
"tqdm",
"watchdog",
]


intersphinx_mapping = {
    "arrow": ("http://arrow.readthedocs.io/en/latest", "arrow.inv"),
    "flask": ("http://flask.pocoo.org/docs/0.12", "flask.inv"),
    "numpy": ("http://docs.scipy.org/doc/numpy-1.13.0", "numpy.inv"),
    "python": ("http://docs.python.org/3.6", "python.inv"),
    "werkzeug": ("http://werkzeug.pocoo.org/docs/0.14", "werkzeug.inv"),
    }

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- nbsphinx options --------------------------------------------------------

nbsphinx_execute = "never" if "READTHEDOCS" in os.environ else "always"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ["_static"]

def warn_undocumented_members(app, what, name, obj, options, lines):
    if what not in [] and len(lines) == 0:
        print("WARNING: %s is undocumented: %s" % (what, name))
        lines.append(".. Warning:: %s '%s' undocumented" % (what, name))

def setup(app):
    app.connect("autodoc-process-docstring", warn_undocumented_members);

