# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with :ref:`trials`."""

import logging

import arrow
import bson.objectid
import gridfs
import pymongo
import numpy
import six

import samlab

log = logging.getLogger(__name__)


def create(database, fs, name, attributes=None, content=None, tags=None):
    """Add a new trial to the :ref:`database <database>`.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    fs: :class:`gridfs.GridFS`, required
    name: string, required
        Human-readable trial name.
    attributes: dict, optional
        Optional metadata to be stored with this trial.  Be sure to pass this
        data through :func:`samlab.serialize.attributes` to ensure that it only
        contains types that can be stored in the database.
    content: dict, optional
        Dict containing content to be stored for this model.  The value for
        each key-value pair in the content should be created using functions in
        :mod:`samlab.serialize`.
    tags: list of str, optional
        Tags to be stored with this trial.

    Returns
    -------
    id: :class:`bson.objectid.ObjectId`
        Unique database identifier for the newly created trial.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
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
    }

    database.trials.create_index("tags")
    database.trials.create_index([("$**", pymongo.TEXT)])
    return database.trials.insert_one(document).inserted_id


def delete(database, fs, tid):
    """Delete a trial from the :ref:`database <database>`.

    Note that this implicitly deletes any models and data owned by the trial.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    fs: :class:`gridfs.GridFS`, required
    tid: :class:`bson.objectid.ObjectId`, required
        Unique database identifier for the trial to be deleted.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(tid, bson.objectid.ObjectId))

    # Delete favorites pointing to models owned by this trial
    for model in database.models.find({"trial": tid}):
        database.favorites.delete_many({"otype": "models", "oid": str(model["_id"])})
    # Delete content owned by models owned by this trial
    for model in database.models.find({"trial": tid}):
        for key, value in model["content"].items():
            fs.delete(value["data"])
    # Delete models owned by this trial
    database.models.delete_many({"trial": tid})
    # Delete favorites pointing to this trial
    database.favorites.delete_many({"otype": "trials", "oid": str(tid)})
    # Delete content owned by this trial
    for trial in database.trials.find({"_id": tid}):
        if "content" in trial: # Early trials didn't have content
            for key, value in trial["content"].items():
                fs.delete(value["data"])
    # Delete the trial
    database.trials.delete_many({"_id": tid})


def mean_loss(results):
    """Deprecated, use :func:`samlab.train.mean_loss` instead."""
    samlab.deprecated("samlab.trial.mean_loss() is deprecated, use :func:`samlab.train.mean_loss` instead.")
    losses = [result["validation-losses"].min() for result in results if "validation-losses" in result and not numpy.any(numpy.isnan(result["validation-losses"]))]
    return numpy.mean(losses) if len(losses) else None


