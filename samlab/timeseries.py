# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for timeseries data in the database."""

import logging
import numbers

import arrow
import bson.objectid
import gridfs
import pymongo

import samlab.database

log = logging.getLogger(__name__)


def add_scalar(database, fs, key, series, step, value):
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(key, str))
    assert(isinstance(series, str))
    assert(isinstance(step, numbers.Number))

    document = {
        "key": key,
        "series": series,
        "step": step,
        "value": value,
        "timestamp": arrow.utcnow().datetime,
        }

    document["_id"] = database.timeseries.insert_one(document).inserted_id

    return document


def delete(database, fs, key, series=None):
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(key, str))

    document = {"key": key}
    if series is not None:
        document["series"] = series
    database.timeseries.delete_many(document)


class Writer(object):
    def __init__(self, key=None, trial=None, database_name="samlab", database_uri="mongodb://localhost:27017", database_replicaset="samlab", dashboard_uri="http://127.0.0.1:4000"):

        if key is None:
            key = "default"

        if trial is None:
            trial = arrow.now().format("YYYY-MM-DDTHH-mm-ss")

        self._key = key
        self._trial = trial
        self._database_name = database_name
        self._database_uri = database_uri
        self._database_replicaset = database_replicaset
        self._dashboard_uri = dashboard_uri
        self._database, self._fs = samlab.database.connect(database_name, database_uri, database_replicaset)

    def __repr__(self):
        return "samlab.dashboard.Connection(key=%r, trial=%r, database_name=%r, database_uri=%r, database_replicaset=%r, dashboard_uri=%r)" % (self._key, self._trial, self._database_name, self._database_uri, self._database_replicaset, self._dashboard_uri)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    @property
    def database_name(self):
        return self._database_name

    @property
    def database_uri(self):
        return self._database_uri

    @property
    def database_replicaset(self):
        return self._database_replicaset

    @property
    def dashboard_uri(self):
        return self._dashboard_uri

    def add_scalar(self, key, step, value):
        samlab.timeseries.add_scalar(self._database, self._fs, self._key + "/" + key, self._trial, step, value)

    def open_browser(self):
        """Open a web browser pointed to the running server."""
        webbrowser.open(self._dashboard_uri)

    def close(self):
        """Close the connection to the Samlab dashboard server.

        Raises
        ------
        RuntimeError, if called more than once, or called on an instance used as a context manager.
        """
        if not self._database:
            raise RuntimeError("Dashboard connection already closed.")

        self._database = None
        self._fs = None
        self._experiment = None
