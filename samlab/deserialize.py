# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Deserializes objects stored in the :ref:`database`."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os
import tempfile

#import gridfs
import numpy
import PIL.Image


log = logging.getLogger(__name__)


def any(fs, content):
    """Deserialize any data stored in the database.

    Parameters
    ----------
    fs: :class:`gridfs.GridFS` instance, required

    content: dict, required
        Content object stored as part of an :ref:`observation <observations>` or :ref:`artifact <artifacts>`.

    Returns
    -------
    array: :class:`numpy.ndarray`
    """
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(content, dict))
    assert("content-type" in content)

    return content["content-type"], fs.get(content["data"])


def array(fs, content):
    """Deserialize a Numpy array stored in the database.

    Parameters
    ----------
    fs: :class:`gridfs.GridFS` instance, required

    content: dict, required
        Content object stored as part of an :ref:`observation <observations>` or :ref:`artifact <artifacts>`.

    Returns
    -------
    array: :class:`numpy.ndarray`
    """
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(content, dict))
    assert("content-type" in content)
    assert(content["content-type"] == "application/x-numpy-array")

    return numpy.load(fs.get(content["data"]))


def arrays(fs, content):
    """Deserialize a collection of Numpy arrays stored in the database.

    Parameters
    ----------
    fs: :class:`gridfs.GridFS` instance, required

    content: dict, required
        Content object stored as part of an :ref:`observation <observations>` or :ref:`artifact <artifacts>`.

    Returns
    -------
    array: :class:`numpy.NpzFile`
    """
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(content, dict))
    assert("content-type" in content)
    assert(content["content-type"] == "application/x-numpy-arrays")

    return numpy.load(fs.get(content["data"]))


def image(fs, content):
    """Deserializes an image stored in the database.

    Parameters
    ----------
    fs: :class:`gridfs.GridFS` instance, required

    content: dict, required
        Content object stored as part of an :ref:`observation <observations>` or :ref:`artifact <artifacts>`.

    Returns
    -------
    image: :class:`PIL.Image.Image`
    """
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(content, dict))
    assert("content-type" in content)
    assert(content["content-type"] in ["image/jpeg", "image/png"])

    return PIL.Image.open(fs.get(content["data"]))


