# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with :ref:`models`."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import arrow
import bson.objectid
import pymongo
import six


log = logging.getLogger(__name__)


def create(database, fs, trial, name, attributes=None, content=None, tags=None):
    """Add a new model to the :ref:`database <database>`.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    fs: :class:`gridfs.GridFS`, required
    trial: :class:`bson.objectid.ObjectId`, required
        ID of the trial that will own this model.
    name: string, required
        Human-readable model name.
    attributes: dict, optional
        Optional metadata to be stored with this model.  Be sure to pass this
        data through :func:`samlab.serialize.attributes` to ensure that it only
        contains types that can be stored in the database.
    content: dict, optional
        Dict containing content to be stored for this model.  The value for
        each key-value pair in the content should be created using functions in
        :mod:`samlab.serialize`.
    tags: list of str, optional
        Tags to be stored with this model.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(trial, bson.objectid.ObjectId))
    assert(isinstance(name, six.string_types))

    if attributes is None:
        attributes = {}
    assert(isinstance(attributes, dict))

    if content is None:
        content = {}
    assert(isinstance(content, dict))
    content = {key: {"data": fs.put(value["data"]), "content-type": value["content-type"], "filename": value.get("filename", None)} for key, value in content.items()}

    if tags is None:
        tags = []
    assert(isinstance(tags, list))
    for tag in tags:
        assert(isinstance(tag, six.string_types))

    document = {
        "attributes": attributes,
        "content": content,
        "created": arrow.utcnow().datetime,
        "name": name,
        "tags": tags,
        "trial": trial,
    }

    return database.models.insert_one(document).inserted_id


def delete(database, fs, mid):
    """Delete a model from the :ref:`database <database>`.

    Note that this implicitly deletes any data owned by the model.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    fs: :class:`gridfs.GridFS`, required
    mid: :class:`bson.objectid.ObjectId`, required
        Unique database identifier for the model to be deleted.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(mid, bson.objectid.ObjectId))

    # Delete favorites pointing to this model
    database.favorites.delete_many({"otype": "models", "oid": str(mid)})
    # Delete content owned by this model
    for model in database.models.find({"_id": mid}):
        for key, value in model["content"].items():
            fs.delete(value["data"])
    # Delete the model
    database.models.delete_many({"_id": mid})


