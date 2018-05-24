# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Deserializes objects stored in the :ref:`database`."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os
import tempfile

import gridfs
import numpy
import PIL.Image


log = logging.getLogger(__name__)


def array(fs, content):
    """Deserialize a Numpy array stored in the database.

    Parameters
    ----------
    fs: :class:`gridfs.GridFS` instance, required

    content: dict, required
        Content object stored as part of an :ref:`observation <observations>` or :ref:`model <models>`.

    Returns
    -------
    array: :class:`numpy.ndarray`
    """
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(content, dict))
    assert("content-type" in content)
    assert(content["content-type"] == "application/x-numpy-array")

    return numpy.load(fs.get(content["data"]))


def image(fs, content):
    """Deserializes an image stored in the database.

    Parameters
    ----------
    fs: :class:`gridfs.GridFS` instance, required

    content: dict, required
        Content object stored as part of an :ref:`observation <observations>` or :ref:`model <models>`.

    Returns
    -------
    image: :class:`PIL.Image.Image`
    """
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(content, dict))
    assert("content-type" in content)
    assert(content["content-type"] in ["image/jpeg", "image/png"])

    return PIL.Image.open(fs.get(content["data"]))


def keras_model(fs, content):
    """Deserialize a Keras model stored in the database.

    Parameters
    ----------
    fs: :class:`gridfs.GridFS` instance, required

    content: dict, required
        Content object stored as part of an :ref:`observation <observations>` or :ref:`model <models>`.

    Returns
    -------
    model: `keras.engine.training.Model`
    """
    import tensorflow.contrib.keras as keras

    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(content, dict))
    assert("content-type" in content)
    assert(content["content-type"] == "application/x-keras-model")

    fd, model_path = tempfile.mkstemp(suffix=".hdf5")
    os.close(fd)

    with open(model_path, "wb") as stream:
        stream.write(fs.get(content["data"]).read())

    model = keras.models.load_model(model_path)
    os.remove(model_path)
    return model
