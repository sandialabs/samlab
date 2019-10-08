# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with :ref:`experiments`."""

import logging

import arrow
import bson.objectid
import gridfs
import pymongo
import six

import samlab

log = logging.getLogger(__name__)


def create(database, fs, name, attributes=None, content=None, tags=None):
    """Add a new experiment to the :ref:`database <database>`.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    fs: :class:`gridfs.GridFS`, required
    name: string, required
        Human-readable experiment name.
    attributes: dict, optional
        Optional metadata to be stored with this experiment.  Be sure to pass this
        data through :func:`samlab.serialize.attributes` to ensure that it only
        contains types that can be stored in the database.
    content: dict, optional
        Dict containing content to be stored for this artifact.  The value for
        each key-value pair in the content should be created using functions in
        :mod:`samlab.serialize`.
    tags: list of str, optional
        Tags to be stored with this experiment.

    Returns
    -------
    id: :class:`bson.objectid.ObjectId`
        Unique database identifier for the newly created experiment.
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

    return database.experiments.insert_one(document).inserted_id


def delete(database, fs, tid):
    """Delete a experiment from the :ref:`database <database>`.

    Note that this implicitly deletes any artifacts and data owned by the experiment.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    fs: :class:`gridfs.GridFS`, required
    tid: :class:`bson.objectid.ObjectId`, required
        Unique database identifier for the experiment to be deleted.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(tid, bson.objectid.ObjectId))

    # Delete favorites pointing to artifacts owned by thisexperiment 
    for artifact in database.artifacts.find({"experiment": tid}):
        database.favorites.delete_many({"otype": "artifacts", "oid": str(artifact["_id"])})
    # Delete content owned by artifacts owned by thisexperiment 
    for artifact in database.artifacts.find({"experiment": tid}):
        for key, value in artifact["content"].items():
            fs.delete(value["data"])
    # Delete artifacts owned by thisexperiment 
    database.artifacts.delete_many({"experiment": tid})
    # Delete favorites pointing to thisexperiment 
    database.favorites.delete_many({"otype": "experiments", "oid": str(tid)})
    # Delete content owned by this experiment
    for experiment in database.experiments.find({"_id": tid}):
        for key, value in experiment["content"].items():
            fs.delete(value["data"])
    # Delete the experiment
    database.experiments.delete_many({"_id": tid})


