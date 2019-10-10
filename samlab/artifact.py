# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with :ref:`artifacts`."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import arrow
import bson.objectid
import gridfs
import pymongo

import samlab.object

log = logging.getLogger(__name__)


def create(database, fs, experiment, name, attributes=None, content=None, tags=None):
    """Add a new artifact to the :ref:`database <database>`.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    fs: :class:`gridfs.GridFS`, required
    experiment: :class:`bson.objectid.ObjectId` or dict, required
        Experiment document or id of the experiment that will own this artifact.
    name: string, required
        Human-readable artifact name.
    attributes: dict, optional
        Optional metadata to be stored with this artifact.  Be sure to pass this
        data through :func:`samlab.serialize.attributes` to ensure that it only
        contains types that can be stored in the database.
    content: dict, optional
        Dict containing content to be stored for this artifact.  The value for
        each key-value pair in the content should be created using functions in
        :mod:`samlab.serialize`.
    tags: list of str, optional
        Tags to be stored with this artifact.

    Returns
    -------
    document: dict
        Newly created artifact document, including the assigned id.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    eid = samlab.object.require_objectid(experiment)
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
        "experiment": eid,
    }

    document["_id"] = database.artifacts.insert_one(document).inserted_id

    return document


def delete(database, fs, artifact):
    """Delete a artifact from the :ref:`database <database>`.

    Note that this implicitly deletes any data owned by the artifact.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    fs: :class:`gridfs.GridFS`, required
    artifact: :class:`bson.objectid.ObjectId` or dict, required
        Artifact document or id of the artifact to be deleted.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    aid = samlab.object.require_objectid(artifact)

    # Delete favorites pointing to this artifact.
    database.favorites.delete_many({"otype": "artifacts", "oid": str(aid)})
    # Delete content owned by this artifact.
    for artifact in database.artifacts.find({"_id": aid}):
        for key, value in artifact["content"].items():
            fs.delete(value["data"])
    # Delete the artifact.
    database.artifacts.delete_many({"_id": aid})


def set_attributes(database, fs, artifact, attributes):
    samlab.object.set_attributes(database, fs, "artifacts", artifact, attributes)


def set_content(database, fs, artifact, key, value):
    samlab.object.set_content(database, fs, "artifacts", artifact, key, value)


def set_name(database, fs, artifact, name):
    samlab.object.set_name(database, fs, "artifacts", artifact, name)


def set_tags(database, fs, artifact, tags):
    samlab.object.set_tags(database, fs, "artifacts", artifact, tags)
