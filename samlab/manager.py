# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working programmatically with the :ref:`manager`."""

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
    """Create an instance of :ref:`manager` for unit tests and tutorials.

    For your real work you will likely want to setup and administer a dedicated
    instance of Samlab Manager; this class makes it easy to start a temporary
    instance for use in tutorials and our unit tests::

        >>> database = samlab.database.Server()
        >>> manager = samlab.manager.Server(database="testing", uri=database.uri)

        ... Use the manager here ...

        >>> manager.stop()
        >>> database.stop()

    Alternatively, you can use the server object as a context manager for automatic cleanup::

        >>> with samlab.database.Server() as database:
        >>>     with samlab.manager.Server(database="testing", uri=database.uri) as manager:
        ...         ... Use the manager here ...

        >>> # Both servers are automatically cleaned-up outside the `with` block.


    Parameters
    ----------
    database: string, required
        Name of a MongoDB database.  The database will be created automatically if it doesn't exist.
    uri: string, required
        URI of a running MongoDB server.
    host: string, optional
        Host interface for binding.  Defaults to localhost to prevent outside connections.
    port: int, optional
        Port for binding.  Defaults to a randomly-chosen open port.
    quiet: bool, optional
        if `True` (the default), suppresses output from the samlab manager process.
    """
    def __init__(self, database, uri, host=None, port=None, quiet=True):
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

        # Start the gpu task queue
        command = ["huey_consumer", "samlab.tasks.gpu.run.queue"]
        log.info("Starting gpu task queue: %s", " ".join(command))
        env = copy.deepcopy(os.environ)
        env["SAMLAB_QUEUE_NAME"] = "samlab-gpu-0"
        env["CUDA_VISIBLE_DEVICES"] = "0"
        self._gpu_task_queue = subprocess.Popen(command, env=env, stdout=output, stderr=output)

        # Start the server
        command = ["samlab-manager", "--database", database, "--database-uri", uri, "--host", host, "--port", str(port)]
        log.info("Starting Samlab manager: %s", " ".join(command))
        self._server = subprocess.Popen(command, stdout=output, stderr=output)

        self._database = database
        self._uri = uri
        self._host = host
        self._port = port

    def __repr__(self):
        return "samlab.manager.Server(database=%r, uri=%r, host=%r, port=%r)" % (self._database, self._uri, self._host, self._port)

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
        """Open a web browser pointed to the running manager."""
        for i in range(10):
            try:
                requests.get(self.uri + "/ready", proxies={"http": None})
                webbrowser.open(self.uri)
                return
            except:
                time.sleep(1.0)
        raise RuntimeError("Couldn't connect to samlab-manager server.")

    def stop(self):
        """Stop the running samlab-manager instance.

        Raises
        ------
        RuntimeError, if called more than once, or called on an instance used a as a context manager.
        """
        if not self._server:
            raise RuntimeError("samlab-manager server already stopped.")

        log.info("Stopping Samlab manager.")
        self._server.terminate()
        self._server.wait()
        self._server = None
        log.info("Samlab manager stopped.")

        log.info("Stopping gpu task queue.")
        self._gpu_task_queue.terminate()
        self._gpu_task_queue.wait()
        self._gpu_task_queue = None
        log.info("GPU task queue stopped.")

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
