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
import six

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


def set_content(database, fs, otype, oid, key, value):
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(otype in ["observations", "experiments", "artifacts"])
    assert(isinstance(oid, bson.objectid.ObjectId))
    assert(isinstance(key, six.string_types))
    assert(isinstance(value, dict))

    obj = database[otype].find_one({"_id": oid})
    if obj is None:
        raise KeyError()
    content = obj["content"]

    # Delete existing content, if any
    if key in content:
        fs.delete(content[key]["data"])
        del content[key]

    content[key] = {"data": fs.put(value["data"]), "content-type": value["content-type"], "filename": value.get("filename", None)}
    database[otype].update_one({"_id": oid}, {"$set": {"content": content}})


def delete_content(database, fs, otype, oid, key):
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(otype in ["observations", "experiments", "artifacts"])
    assert(isinstance(oid, bson.objectid.ObjectId))
    assert(isinstance(key, six.string_types))

    obj = database[otype].find_one({"_id": oid})
    if obj is None:
        raise KeyError()
    content = obj["content"]

    # Delete existing content, if any
    if key in content:
        fs.delete(content[key]["data"])
        del content[key]

    database[otype].update_one({"_id": oid}, {"$set": {"content": content}})


def set_attributes(database, fs, otype, oid, attributes):
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(otype in ["observations", "experiments", "artifacts"])
    assert(isinstance(oid, bson.objectid.ObjectId))
    assert(isinstance(attributes, dict))

    obj = database[otype].find_one({"_id": oid})
    if obj is None:
        raise KeyError()

    database[otype].update_one({"_id": oid}, {"$set": {"attributes": attributes}})


def update_attributes(database, fs, otype, oid, new_attributes):
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(otype in ["observations", "experiments", "artifacts"])
    assert(isinstance(oid, bson.objectid.ObjectId))
    assert(isinstance(new_attributes, dict))

    obj = database[otype].find_one({"_id": oid})
    if obj is None:
        raise KeyError()

    attributes = obj["attributes"]
    attributes.update(new_attributes)
    database[otype].update_one({"_id": oid}, {"$set": {"attributes": attributes}})


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
    assert(isinstance(search, six.string_types))

    visitor = samlab.search.parser().parse(search).accept(_IdSearchVisitor(database[otype]))
    return visitor.ids
