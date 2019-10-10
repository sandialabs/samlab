# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with generic objects (observations, experiments, and artifacts)."""

import logging
import numbers

import arrow
import bson.objectid
import gridfs
import pymongo

log = logging.getLogger(__name__)


def add_scalar(database, fs, key, step, value):
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(key, str))
    assert(isinstance(step, numbers.Number))

    document = {
        "key": key,
        "step": step,
        "value": value,
        "timestamp": arrow.utcnow().datetime,
        }

    document["_id"] = database.timeseries.insert_one(document).inserted_id

    return document
