# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Serializes objects for storage in the :ref:`database`."""

from __future__ import absolute_import, division, print_function, unicode_literals

import io
import inspect
import json as pyjson
import logging
import os
import tempfile

import numpy
import pymongo
import six


log = logging.getLogger(__name__)


def array(value):
    """Serialize a numpy array for storage in the database.

    Parameters
    ----------
    value: :class:`numpy.ndarray` or array-like object, required
        The array to be serialized.

    Returns
    -------
    content: dict
        Serialized in-memory representation of the array that can be used with :func:`samlab.observation.create`, :func:`samlab.observation.create_many`, :func:`samlab.trial.create`, and :func:`samlab.model.create`.
    """
    stream = io.BytesIO()
    numpy.save(stream, value)
    return {
        "data": stream.getvalue(),
        "content-type": "application/x-numpy-array",
    }


def arrays(*args, **kwargs):
    """Serialize multiple numpy arrays for storage in the database.

    Returns
    -------
    content: dict
        Serialized in-memory representation of the arrays that can be used with :func:`samlab.observation.create`, :func:`samlab.observation.create_many`, :func:`samlab.trial.create`, and :func:`samlab.model.create`.
    """
    stream = io.BytesIO()
    numpy.savez(stream, *args, **kwargs)
    return {
        "data": stream.getvalue(),
        "content-type": "application/x-numpy-arrays",
    }


def attributes(value):
    """Copy an arbitrary data structure with modifications so it can be stored in the database.

    :ref:`observations`, :ref:`trials`, and :ref:`models` are all entities that
    can include "attributes" (arbitrary metadata).  Use this function to clean
    attribute contents before passing them to Samlab, to filter-out unserializable
    types such as functions.

    Parameters
    ----------
    value: arbitrary Python value, required
        The value to be copied.

    Returns
    -------
    serializable: modified copy of `value` that can be used with :func:`samlab.observation.create`, :func:`samlab.observation.create_many`, :func:`samlab.trial.create`, and :func:`samlab.model.create`.
    """
    def valid_key(key):
        if key.startswith("$"):
            return key[1:]
        return key

    if isinstance(value, list):
        return [attributes(v) for v in value]
    if isinstance(value, tuple):
        return tuple([attributes(v) for v in value])
    if isinstance(value, dict):
        return {valid_key(key): attributes(value) for key, value in value.items()}
    if inspect.isfunction(value):
        return "<function %s%s>" % (value.__module__ + "." if value.__module__ else "", value.__name__)
    return value


def image(img):
    """Serialize an in-memory or on-disk image for storage in the database.

    Parameters
    ----------
    img: str or :class:`PIL.Image.Image`, required

    Returns
    -------
    content: dict
        Serialized in-memory representation of the image that can be used with :func:`samlab.observation.create`, :func:`samlab.observation.create_many`, :func:`samlab.trial.create`, and :func:`samlab.model.create`.
    """
    import PIL.Image

    if isinstance(img, six.string_types):
        path = img
        base_path, extension = os.path.splitext(path)
        extension = extension.lower()
        if extension in [".jpg", ".jpeg"]:
            data = open(path, "rb")
            content_type = "image/jpeg"
        elif extension in [".png"]:
            data = open(path, "rb")
            content_type = "image/png"
        else:
            raise ValueError("Unknown image type: %s" % path)
    elif isinstance(img, PIL.Image.Image):
        path = None
        buffer = io.BytesIO()
        img.save(buffer, format="jpeg", quality=95)
        data = buffer.getvalue()
        content_type = "image/jpeg"
    else:
        raise ValueError("Unknown image type: %s" % img)

    return { "data": data, "content-type": content_type, "filename": path }


def json(document, content_type="application/json"):
    """Serialize a JSON document for storage in the database.

    Parameters
    ----------
    document: json-compatible data stucture

    Returns
    -------
    content: dict
        Serialized in-memory representation of the document that can be used with :func:`samlab.observation.create`, :func:`samlab.observation.create_many`, :func:`samlab.trial.create`, and :func:`samlab.model.create`.
    """
    return {
        "data": pyjson.dumps(document).encode("utf8"),
        "content-type": content_type,
    }


def obj_mesh(path):
    return generic_path(path, content_type="application/x-wavefront-obj")


def generic_path(path, content_type):
    assert(isinstance(path, six.string_types))
    assert(os.path.exists(path))

    return {
        "data": open(path, "rb"),
        "content-type": content_type,
        "filename": path,
    }


def stl_mesh(path):
    return generic_path(path, content_type="model/stl")


def string(value):
    """Serialize a string for storage in the database.

    Parameters
    ----------
    value: str, required

    Returns
    -------
    content: dict
        Serialized version of the string that can be used with :func:`samlab.observation.create`, :func:`samlab.observation.create_many`, :func:`samlab.trial.create`, and :func:`samlab.model.create`.
    """
    return {
        "data": value.encode("utf8"),
        "content-type": "text/plain; charset=utf-8",
    }

