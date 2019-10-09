# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with :ref:`observations`."""

from __future__ import absolute_import, division, print_function, unicode_literals

import collections
import copy
import io
import logging

import arrow
import bson
import gridfs
import numpy
import pymongo

import samlab
import samlab.deserialize
import samlab.object
import samlab.serialize

log = logging.getLogger(__name__)


def create(database, fs, attributes=None, content=None, tags=None):
    """Add a new observation to the :ref:`database <database>`.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    fs: :class:`gridfs.GridFS`, required
    attributes: dict, optional
        Optional metadata to be stored with this observation.  Be sure to pass this
        data through :func:`samlab.serialize.attributes` to ensure that it only
        contains types that can be stored in the database.
    content: dict, optional
        Dict containing content to be stored for this observation.  The value for
        each key-value pair in the content should be created using functions in
        :mod:`samlab.serialize`.
    tags: list of str, optional
        Tags to be stored with this observation.

    Returns
    -------
    :class:`bson.objectid.ObjectId`
        Unique identifier for the observation.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))

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
        "tags": tags,
    }

    return database.observations.insert_one(document).inserted_id


def create_many(database, fs):
    """Return a context object that can add multiple observations to the :ref:`database <database>`.

    Examples
    --------

    >>> with samlab.observation.create_many(database, fs) as observations:
        observations.create(...)
        observations.create(...)
        .
        .
        .
        observations.create(...)

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    fs: :class:`gridfs.GridFS`, required
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))

    class Implementation(object):
        def __init__(self, database, fs):
            self._database = database
            self._fs = fs
            self._created = arrow.utcnow().datetime

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def create(self, attributes=None, content=None, tags=None):
            """Add an observation to the :ref:`database <database>`.

            Parameters
            ----------
            attributes: dict, optional
                Optional metadata to be stored with this observation.  Be sure to pass this
                data through :func:`samlab.serialize.attributes` to ensure that it only
                contains types that can be stored in the database.
            content: dict, optional
                Dict containing content to be stored for this observation.  The value for
                each key-value pair in the content should be created using functions in
                :mod:`samlab.serialize`.
            tags: list of str, optional
                Tags to be stored with this observation.

            Returns
            -------
            :class:`bson.objectid.ObjectId`
                Unique identifier for the observation.
            """
            if attributes is None:
                attributes = {}
            assert(isinstance(attributes, dict))

            if content is None:
                content = {}
            assert(isinstance(content, dict))
            content = {key: {"data": self._fs.put(value["data"]), "content-type": value["content-type"], "filename": value.get("filename", None)} for key, value in content.items()}

            if tags is None:
                tags = []
            assert(isinstance(tags, list))
            for tag in tags:
                assert(isinstance(tag, str))

            document = {
                "attributes": attributes,
                "content": content,
                "created": self._created,
                "tags": tags,
            }

            oid = self._database.observations.insert_one(document).inserted_id
            return oid

    return Implementation(database, fs)


def delete(database, fs, oid):
    """Delete an observation from the :ref:`database <database>`.

    Note that this implicitly deletes any data owned by the observation.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    fs: :class:`gridfs.GridFS`, required
    oid: :class:`bson.objectid.ObjectId`, required
        Unique database identifier for the observation to be deleted.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(oid, bson.objectid.ObjectId))

    # Delete favorites pointing to this observation
    database.favorites.delete_many({"otype": "observations", "oid": str(oid)})
    # Delete content owned by this observation
    for observation in database.observations.find({"_id": oid}):
        for key, value in observation["content"].items():
            fs.delete(value["data"])
    # Delete the observation
    database.observations.delete_many({"_id": oid})


def update(database, fs, updater, filter=None, sort=None):
    """Make changes to observations stored in the database.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required.
    filter: filter specification compatible with :meth:`pymongo.collection.Collection.find`, optional.
    sort: sort specification compatible with :meth:`pymongo.collection.Collection.find`, optional.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))

    if filter is None:
        filter = {}

    cursor = database.observations.find(filter=filter, sort=sort)

    for original in cursor:
        modified = updater(copy.deepcopy(original))

        if modified is not None:
            if modified["_id"] != original["_id"]:
                raise ValueError("Cannot change observation ID.")
            if modified["created"] != original["created"]:
                raise ValueError("Cannot change observation creation timestamp.")

            modified["tags"] = list(set(modified["tags"]))

            change = {"$set": {}}
            if modified["attributes"] != original["attributes"]:
                change["$set"]["attributes"] = modified["attributes"]
            if modified["content"] != original["content"]:
                for key, value in modified["content"].items():
                    if not isinstance(value["data"], bson.objectid.ObjectId):
                        value["data"] = fs.put(value["data"])
                change["$set"]["content"] = modified["content"]
            if modified["tags"] != original["tags"]:
                change["$set"]["tags"] = modified["tags"]

            if change["$set"]:
                change["$set"]["modified"] = arrow.utcnow().datetime

            if change["$set"]:
                database.observations.update_one({"_id": original["_id"]}, change)
                #changes.append(pymongo.UpdateOne({"_id": original["_id"]}, change))


def set_tag(database, tag, state, filter=None, sort=None):
    """Add or remove observation tags using the caller's criteria.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required.
    tag: str, required
        The tag to be set or cleared.
    state: True, False, or a callable, required.
        If True, add `tag` to all observations matched by `filter`.  If False, remove `tag` from all
        observations matched by `filter`.  Otherwise call `state` with each observation matched by `filter`,
        adding `tag` when `state` returns True and removing `tag` if `state` returns False.
    filter: filter specification compatible with :meth:`pymongo.collection.Collection.find`, optional.
    sort: sort specification compatible with :meth:`pymongo.collection.Collection.find`, optional.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(tag, str))

    if filter is None:
        filter = {}

    if state is True:
        database.observations.update_many(filter=filter, update={"$addToSet": {"tags": tag}})
        log.info("Added tag %s to %s observations." % (tag, database.observations.count(filter=filter)))

    elif state is False:
        database.observations.update_many(filter=filter, update={"$pull": {"tags": tag}})
        log.info("Removed tag %s from %s observations." % (tag, database.observations.count(filter=filter)))

    else:
        if sort is None:
            sort = [("_id", pymongo.ASCENDING)]

        cursor = database.observations.find(filter=filter, sort=sort)

        add_tags = []
        remove_tags = []
        for observation in cursor:
            if state(observation):
                add_tags.append(pymongo.UpdateOne({"_id": observation["_id"]}, {"$addToSet": {"tags": tag}}))
            else:
                remove_tags.append(pymongo.UpdateOne({"_id": observation["_id"]}, {"$pull": {"tags": tag}}))

        if add_tags:
            database.observations.bulk_write(add_tags)
        if remove_tags:
            database.observations.bulk_write(remove_tags)
        log.info("Set tag %s on %s of %s observations." % (tag, len(add_tags), cursor.count()))


def resize_images(database, size, target_key, source_key="original", filter=None, overwrite=False):
    """Add resized images to existing observations

    Use this function to resize / resample images when the originals aren't the
    correct size for training.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required.
    size: tuple, required
        (width, height) tuple containing the desired image size.
    target_key: str, required
        Name of the key that will store the resized images.
    source_key: str, optional
        Name of the key that contains the existing images to be resized.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(size, tuple))
    assert(len(size) == 2)
    assert(isinstance(target_key, str))
    assert(isinstance(source_key, str))

    import PIL.Image

    fs = gridfs.GridFS(database)

    cursor = database.observations.find(filter=filter)

    progress = samlab.Progress(
        total=cursor.count(),
        step_message="Completed image resizing for {count} of {total} observations in {elapsed:.1f}s ({rate:.2f} observations/s).",
        log=log,
        )

    requests = []
    for observation in cursor:
        content = dict(observation["content"]) # Force a deep-copy

        if target_key in content and not overwrite:
            continue

        try:
            image = samlab.deserialize.image(fs, content[source_key])
        except Exception as e:
            log.error("Couldn't load observation %s image %s: %s", observation["_id"], content[source_key], e)
            continue
        image = image.resize(size, resample=PIL.Image.BICUBIC)
        content[target_key] = samlab.serialize.image(image)
        content[target_key]["data"] = fs.put(content[target_key]["data"])

        requests.append(pymongo.UpdateOne({"_id": observation["_id"]}, {"$set": {"content": content}}))

        progress.step()

    database.observations.bulk_write(requests)
    progress.finish()


