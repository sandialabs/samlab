# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working programmatically with the :ref:`dashboard`."""

from __future__ import absolute_import, division, print_function, unicode_literals

import contextlib
import copy
import logging
import os
import socket
import subprocess
import time
import webbrowser

import requests

log = logging.getLogger(__name__)


class Server(object):
    """Create an instance of :ref:`dashboard` for unit tests and tutorials.

    For your real work you will likely want to setup and administer a dedicated
    instance of the Samlab dashboard server; this class makes it easy to start a temporary
    instance for use in tutorials and our unit tests::

        >>> database = samlab.database.Server()
        >>> server = samlab.dashboard.Server(database="testing", uri=database.uri, replicaset=database.replicaset)

        ... Use the server here ...

        >>> server.stop()
        >>> database.stop()

    Alternatively, you can use the server object as a context manager for automatic cleanup::

        >>> with samlab.database.Server() as database:
        >>>     with samlab.dashboard.Server(database="testing", uri=database.uri, replicaset=database.replicaset) as server:
        ...         ... Use the server here ...

        >>> # Both servers are automatically cleaned-up outside the `with` block.


    Parameters
    ----------
    database_name: string, required
        Name of a MongoDB database.  The database will be created automatically if it doesn't exist.
    database_uri: string, required
        URI of a running MongoDB server.
    database_replicaset: string, required
        Name of an existing server replica set.
    host: string, optional
        Host interface for binding.  Defaults to localhost to prevent outside connections.
    port: int, optional
        Port for binding.  Defaults to a randomly-chosen open port.
    quiet: bool, optional
        if `True` (the default), suppresses output from the samlab server process.
    """
    def __init__(self, database_name, database_uri, database_replicaset, host=None, port=None, quiet=True):
        # Choose an interface for binding.
        if host is None:
            host = "127.0.0.1"

        # Find an available port.
        if port is None:
            with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                sock.bind((host, 0))
                port = sock.getsockname()[1]

        # Optionally suppress output from the server.
        if quiet:
            output = open(os.devnull, "wb")
        else:
            output = None

        # Start the message queue
        command = ["redis-server", "--bind", "127.0.0.1", "--save", ""]
        log.info("Starting message queue: %s", " ".join(command))
        self._message_queue = subprocess.Popen(command, stdout=output, stderr=output)

        # Start the generic task queue
        command = ["huey_consumer", "samlab.tasks.generic.run.queue"]
        log.info("Starting generic task queue: %s", " ".join(command))
        self._generic_task_queue = subprocess.Popen(command, stdout=output, stderr=output)

        # Start the server
        command = ["samlab-server", "--database-name", database_name, "--database-uri", database_uri, "--database-replicaset", database_replicaset, "--host", host, "--port", str(port)]
        log.info("Starting Samlab server: %s", " ".join(command))
        self._server = subprocess.Popen(command, stdout=output, stderr=output)

        self._database_name = database_name
        self._database_uri = database_uri
        self._database_replicaset = database_replicaset
        self._host = host
        self._port = port

    def __repr__(self):
        return "samlab.server.Server(database_name=%r, database_uri=%r, database_replicaset=%r, host=%r, port=%r)" % (self._database_name, self._database_uri, self._database_replicaset, self._host, self._port)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False

    @property
    def uri(self):
        """Address of the running server that can be used with web clients."""
        return "http://%s:%s" % (self._host, self._port)

    def open_browser(self):
        """Open a web browser pointed to the running server."""
        for i in range(10):
            try:
                requests.get(self.uri + "/ready", proxies={"http": None})
                webbrowser.open(self.uri)
                return
            except:
                time.sleep(1.0)
        raise RuntimeError("Couldn't connect to samlab server.")

    def stop(self):
        """Stop the running samlab-server instance.

        Raises
        ------
        RuntimeError, if called more than once, or called on an instance used a as a context manager.
        """
        if not self._server:
            raise RuntimeError("samlab server already stopped.")

        log.info("Stopping Samlab server.")
        self._server.terminate()
        self._server.wait()
        self._server = None
        log.info("Samlab server stopped.")

        log.info("Stopping generic task queue.")
        self._generic_task_queue.terminate()
        self._generic_task_queue.wait()
        self._generic_task_queue = None
        log.info("Generic task queue stopped.")

        log.info("Stopping message queue.")
        self._message_queue.terminate()
        self._message_queue.wait()
        self._message_queue = None
        log.info("Message queue stopped.")
