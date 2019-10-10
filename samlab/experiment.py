# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with :ref:`experiments`."""

import logging

import arrow
import bson.objectid
import gridfs
import pymongo

import samlab.object

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
        Dict containing content to be stored for this experiment.  The value for
        each key-value pair in the content should be created using functions in
        :mod:`samlab.serialize`.
    tags: list of str, optional
        Tags to be stored with this experiment.

    Returns
    -------
    experiment: dict
        Newly created experiment, including its unique id.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(name, str))

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
        assert(isinstance(tag, str))


    document = {
        "attributes": attributes,
        "content": content,
        "created": arrow.utcnow().datetime,
        "name": name,
        "tags": tags,
    }

    document["_id"] = database.experiments.insert_one(document).inserted_id

    return document


def delete(database, fs, experiment):
    """Delete a experiment from the :ref:`database <database>`.

    Note that this implicitly deletes any artifacts and data owned by the experiment.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    fs: :class:`gridfs.GridFS`, required
    eid: :class:`bson.objectid.ObjectId`, required
        Unique database identifier for the experiment to be deleted.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    eid = samlab.object.require_objectid(experiment)

    # Delete favorites pointing to artifacts owned by this experiment.
    for artifact in database.artifacts.find({"experiment": eid}):
        database.favorites.delete_many({"otype": "artifacts", "oid": str(artifact["_id"])})
    # Delete content owned by artifacts owned by this experiment.
    for artifact in database.artifacts.find({"experiment": eid}):
        for key, value in artifact["content"].items():
            fs.delete(value["data"])
    # Delete artifacts owned by this experiment.
    database.artifacts.delete_many({"experiment": eid})
    # Delete favorites pointing to this experiment.
    database.favorites.delete_many({"otype": "experiments", "oid": str(eid)})
    # Delete content owned by this experiment.
    for experiment in database.experiments.find({"_id": eid}):
        for key, value in experiment["content"].items():
            fs.delete(value["data"])
    # Delete the experiment.
    database.experiments.delete_many({"_id": eid})


def set_attributes(database, fs, experiment, attributes):
    samlab.object.set_attributes(database, fs, "experiments", experiment, attributes)


def set_content(database, fs, experiment, key, value):
    samlab.object.set_content(database, fs, "experiments", experiment, key, value)


def set_name(database, fs, experiment, name):
    samlab.object.set_name(database, fs, "experiments", experiment, name)


def set_tags(database, fs, experiment, tags):
    samlab.object.set_tags(database, fs, "experiments", experiment, tags)
