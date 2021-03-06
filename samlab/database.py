# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with the :ref:`database`."""

from __future__ import absolute_import, division, print_function, unicode_literals

import contextlib
import logging
import os
import shutil
import socket
import subprocess
import tempfile
import time

import gridfs
import pymongo


log = logging.getLogger(__name__)


class Server(object):
    """Create an instance of mongod for unit tests and tutorials.

    For real work you may want to setup and administer a dedicated instance of
    MongoDB; this class makes it easy to start a temporary instance of MongoDB
    for use with tutorials and our unit tests::

        >>> server = samlab.database.Server()
        >>> database = samlab.database.connect(server.uri)

        ... Use the database here ...

        >>> server.stop()

    Alternatively, you can use the server object as a context manager for automatic cleanup::

        >>> with samlab.database.Server() as server:
        ...     database = samlab.database.connect(server.uri)
        ...     ... Use the database here ...

        >>> # Server is automatically cleaned-up outside the `with` block.


    Parameters
    ----------
    dbpath: string, optional
        Filesystem path to a directory for MongoDB storage.  The directory will
        be created automatically if it doesn't already exist.  If left
        unspecified, a temporary directory will be created.
    host: string, optional
        Host interface that mongodb will listen on.  Defaults to localhost to
        prevent outside connections.
    port: int, optional
        Port for binding.  Defaults to a randomly-chosen open port.
    reset: bool, optional
        If `True`, deletes `dbpath` before starting the server.  This is useful
        when running tutorials or unit tests with a specific path.  The default
        is `False` in case you choose to use the server for real experiments.
    quiet: bool, optional
        if `True` (the default), suppresses output from the mongod process.
    """
    def __init__(self, dbpath=None, host=None, port=None, replicaset=None, reset=False, quiet=True):
        # Choose a directory for storage.
        if dbpath is None:
            dbpath=tempfile.mkdtemp()

        # Optionally reset data storage.
        if reset and os.path.exists(dbpath):
            shutil.rmtree(dbpath)

        # Ensure the data storage exists.
        if not os.path.exists(dbpath):
            os.makedirs(dbpath)

        # Choose an interface for binding.
        if host is None:
            host = "127.0.0.1"

        # Find an available port.
        if port is None:
            # Try the default.
            try:
                port = 27017
                with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                    sock.bind((host, port))
            except:
                # Let the OS assign a port.
                with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                    sock.bind((host, 0))
                    port = sock.getsockname()[1]

        # Make sure we have replicaset name.
        if replicaset is None:
            replicaset = "samlab"

        # Optionally suppress output from the server.
        if quiet:
            output = open(os.devnull, "wb")
        else:
            output = None

        # Start the server
        command = ["mongod", "--dbpath", dbpath, "--directoryperdb", "--replSet", replicaset, "--bind_ip", host, "--port", str(port)]
        log.info("Starting database server: %s", " ".join(command))
        self._mongod = subprocess.Popen(command, stdout=output, stderr=output)

        self._dbpath = dbpath
        self._host = host
        self._port = port
        self._replicaset = replicaset
        self._reset = reset

        # Connect the client.
        client = pymongo.MongoClient(self.uri)

        # Look for an existing replica set.
        config = client.local["system.replset"].find_one({"_id": replicaset})

        if config is None:
            # Create a new config from scratch.
            client.admin.command({"replSetInitiate": {"_id": replicaset, "members": [{"_id": 0, "host": "%s:%s" % (host, port)}]}})
        else:
            # Modify the config to match our host and port.
            for member in config["members"]:
                member["host"] = f"{host}:{port}"
            client.admin.command({"replSetReconfig": config, "force": True})

    def __repr__(self):
        return "samlab.database.Server(dbpath=%r, host=%r, port=%r, reset=%r)" % (self._dbpath, self._host, self._port, self._reset)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False

    @property
    def uri(self):
        """MongoDB connection URI that can be used to connect to the running a database.

        Typically, you would pass this as an argument to :func:`samlab.database.connect`.
        """
        return "mongodb://%s:%s" % (self._host, self._port)

    @property
    def replicaset(self):
        return self._replicaset

    def stop(self):
        """Stop the running mongod instance.

        Raises
        ------
        RuntimeError, if called more than once, or called on an instance used a as a context manager.
        """
        if not self._mongod:
            raise RuntimeError("Database server already stopped.")

        log.info("Stopping database server.")
        self._mongod.terminate()
        self._mongod.wait()
        self._mongod = None
        log.info("Database server stopped.")


def connect(name="samlab", uri="mongodb://localhost:27017", replicaset="samlab"):
    """Open a database connection.

    Parameters
    ----------
    name: string, required
        Database name.
    uri: string, optional
        Database uri.
    replicaset: string, optional
        Database replica set.

    Returns
    -------
    database: :class:`pymongo.mongo_client.MongoClient`
        Database connection object.
    fs: :class:`gridfs.GridFS`
        Database file storage object.
    """
    assert(isinstance(name, str))
    assert(isinstance(uri, str))
    assert(isinstance(replicaset, str))

    client = pymongo.MongoClient(uri, replicaset=replicaset)
    database = client[name]
    fs = gridfs.GridFS(database)

    # Force the database into existence, so we can follow change streams.
    with contextlib.suppress(pymongo.errors.CollectionInvalid):
        database.create_collection("artifacts")
    with contextlib.suppress(pymongo.errors.CollectionInvalid):
        database.create_collection("experiments")
    with contextlib.suppress(pymongo.errors.CollectionInvalid):
        database.create_collection("observations")
    with contextlib.suppress(pymongo.errors.CollectionInvalid):
        database.create_collection("layouts")
    with contextlib.suppress(pymongo.errors.CollectionInvalid):
        database.create_collection("timeseries")

    # Create database indexes
    database.layouts.create_index("lid")
    database.artifacts.create_index([("$**", pymongo.TEXT)])
    database.artifacts.create_index("tags")
    database.experiments.create_index([("$**", pymongo.TEXT)])
    database.experiments.create_index("tags")
    database.observations.create_index([("$**", pymongo.TEXT)])
    database.observations.create_index("tags")
    database.timeseries.create_index([("$**", pymongo.TEXT)])
    database.timeseries.create_index("key")

    return database, fs

