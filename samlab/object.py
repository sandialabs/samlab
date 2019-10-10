# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with generic objects (observations, experiments, and artifacts)."""

from __future__ import absolute_import, division, print_function, unicode_literals

import collections.abc
import logging

import arrow
import bson.objectid
import gridfs
import pymongo

import samlab.search

log = logging.getLogger(__name__)


def load(database, otype, filter=None, oids=None):
    """Load database objects of the given type."""
    assert(isinstance(database, pymongo.database.Database))
    assert(otype in ["observations", "experiments", "artifacts"])

    if filter is not None:
        return list(database[otype].find(filter=filter))

    if oids is not None:
        assert(isinstance(oids, collections.abc.Collection))
        return [database[otype].find_one({"_id": oid}) for oid in oids]

    return list(database[otype].find())


def require_objectid(oid):
    if isinstance(oid, dict):
        oid = oid["_id"]
    if not isinstance(oid, bson.objectid.ObjectId):
        raise ValueError("A bson.objectid.ObjectId or MongoDB document with _id field is required.")
    return oid


def set_attributes(database, fs, otype, oid, attributes):
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(otype in ["observations", "experiments", "artifacts"])
    oid = require_objectid(oid)
    assert(isinstance(attributes, dict))

    obj = database[otype].find_one({"_id": oid})
    if obj is None:
        raise KeyError()

    database[otype].update_one({"_id": oid}, {"$set": {"attributes": attributes, "modified": arrow.utcnow().datetime}})


def set_content(database, fs, otype, oid, key, value):
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(otype in ["observations", "experiments", "artifacts"])
    oid = require_objectid(oid)
    assert(isinstance(key, str))
    assert(isinstance(value, (dict, type(None))))

    obj = database[otype].find_one({"_id": oid})
    if obj is None:
        raise KeyError()
    content = obj["content"]

    # Delete existing content, if any
    if key in content:
        fs.delete(content[key]["data"])
        del content[key]

    if value is not None:
        content[key] = {"data": fs.put(value["data"]), "content-type": value["content-type"], "filename": value.get("filename", None)}
    database[otype].update_one({"_id": oid}, {"$set": {"content": content, "modified": arrow.utcnow().datetime}})


def set_name(database, fs, otype, oid, name):
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(otype in ["observations", "experiments", "artifacts"])
    oid = require_objectid(oid)
    assert(isinstance(name, str))

    obj = database[otype].find_one({"_id": oid})
    if obj is None:
        raise KeyError()

    database[otype].update_one({"_id": oid}, {"$set": {"name": name, "modified": arrow.utcnow().datetime}})


def set_tags(database, fs, otype, oid, tags):
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(otype in ["observations", "experiments", "artifacts"])
    oid = require_objectid(oid)
    assert(isinstance(tags, list))

    obj = database[otype].find_one({"_id": oid})
    if obj is None:
        raise KeyError()

    database[otype].update_one({"_id": oid}, {"$set": {"tags": tags, "modified": arrow.utcnow().datetime}})


class _IdSearchVisitor(object):
    def __init__(self, collection):
        self._collection = collection
        self._stack = []

    @property
    def ids(self):
        return list(self._stack[0])

    def visit_and(self, operands):
        current = len(self._stack)
        for operand in operands:
            operand.accept(self)
        result = self._stack.pop()
        while(len(self._stack) > current):
            result &= self._stack.pop()
        self._stack.append(result)

    def visit_not(self, operand):
        operand.accept(self)
        result = set([o["_id"] for o in self._collection.find(projection={"_id": True})])
        result -= self._stack.pop()
        self._stack.append(result)

    def visit_or(self, operands):
        current = len(self._stack)
        for operand in operands:
            operand.accept(self)
        result = self._stack.pop()
        while(len(self._stack) > current):
            result |= self._stack.pop()
        self._stack.append(result)

    def visit_term(self, term):
        # Match documents that contain the search term in text (field values).
        result = set([o["_id"] for o in self._collection.find(filter={"$text": {"$search": '"' + term + '"'}}, projection={"_id": True})])
        # Match documents with content that matches the search term.
        result |= set([o["_id"] for o in self._collection.find(filter={"content." + term: {"$exists": True}}, projection={"_id": True})])
        # Match documents with attribute fields that match the search term.
        result |= set([o["_id"] for o in self._collection.find(filter={"attributes." + term: {"$exists": True}}, projection={"_id": True})])
        # Match documents whose ID matches the search term.
        try:
            oid = bson.objectid.ObjectId(term)
            result |= set([o["_id"] for o in self._collection.find(filter={"_id": oid}, projection={"_id": True})])
        except:
            pass
        self._stack.append(result)


def search(database, otype, search):
    assert(isinstance(database, pymongo.database.Database))
    assert(otype in ["observations", "experiments", "artifacts"])
    assert(isinstance(search, str))

    visitor = samlab.search.parser().parse(search).accept(_IdSearchVisitor(database[otype]))
    return visitor.ids
