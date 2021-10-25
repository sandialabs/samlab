# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import arrow
import contextlib
import itertools
import logging
import os
import signal
import socket
import subprocess
import sys
import time
import webbrowser

import requests

log = logging.getLogger(__name__)

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
bin_dir = os.path.join(root_dir, "bin")


class Server(object):
    """Create an instance of :ref:`dashboard` for unit tests and tutorials.
    For your real work you will likely want to setup and administer a dedicated
    instance of the Samlab dashboard server; this class makes it easy to start a temporary
    instance for use in tutorials and our unit tests::
        >>> server = samlab.dashboard.Server()
        ... Use the server here ...
        >>> server.stop()
        >>> database.stop()
    Alternatively, you can use the server object as a context manager for automatic cleanup::
        >>> with samlab.dashboard.Server() as server:
        ...         ... Use the server here ...
        >>> # Server is automatically cleaned-up when the `with` block is exited.
    Parameters
    ----------
    host: string, optional
        Host interface for binding.  Defaults to localhost to prevent outside connections.
    port: int, optional
        Port for binding.  Defaults to a randomly-chosen open port.
    quiet: bool, optional
        If :any:`True` (the default), suppresses output from the samlab server process.
    """
    def __init__(self, host=None, port=None, config=True, coverage=False, quiet=True):
        # Choose an interface for binding.
        if host is None:
            host = "127.0.0.1"

        # Find an available port.
        if port is None:
            # Try using the default.
            try:
                port = 4000
                with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                    sock.bind((host, port))
            except Exception as e:
                # Ask the OS for an available port.
                with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                    sock.bind((host, 0))
                    port = sock.getsockname()[1]

        # Optionally suppress output from the server.
        if quiet:
            output = open(os.devnull, "wb")
        else:
            output = None

        # Start the server
        command = [
            sys.executable, os.path.join(root_dir, "bin", "samlab-dashboard"),
            "--host", host,
            "--port", str(port),
            "--no-browser",
            ]
        if not config:
            command += ["--no-config"]
        if coverage:
            command += ["--coverage"]
        log.info("Starting dashboard server: %s", " ".join(command))
        self._server = subprocess.Popen(command, stdout=output, stderr=output)

        self._host = host
        self._port = port
        self._config = config
        self._coverage = coverage
        self._quiet = quiet


    def __repr__(self):
        return f"samlab.dashboard.Server(host={self._host!r}, port={self._port!r}, config={self._config!r}, coverage={self._coverage!r}, quiet={self._quiet!r})"


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False


    def browser(self, timeout=None):
        """Open a web browser pointed to the running server."""
        self.ready(timeout=timeout)
        webbrowser.open(self.uri)


    def ready(self, timeout=None):
        """Wait until the server has started and is ready to receive requests."""
        start = time.time()
        while True:
            if timeout and time.time() - start > timeout:
                raise RuntimeError("Timed-out waiting for server.") # pragma: no cover

            try:
                requests.get(self.uri + "/ready", proxies={"http": None})
                return
            except Exception as e:
                time.sleep(1.0)


    def stop(self):
        """Stop the running dashboard server.
        Raises
        ------
        RuntimeError, if called more than once, or called on an instance used as a context manager.
        """
        if not self._server:
            raise RuntimeError("dashboard server already stopped.") # pragma: no cover

        log.info("Stopping dashboard server.")
        self._server.send_signal(signal.SIGINT)
        self._server.wait()
        self._server = None
        log.info("Dashboard server stopped.")


    @property
    def uri(self):
        """Address of the running server that can be used with web clients."""
        return "http://%s:%s" % (self._host, self._port)


class Writer(object):
    def __init__(self, root):
        self._root = os.path.abspath(root)
        self._keys = {}


    def __repr__(self):
        return f"samlab.dashboard.Writer(root={self._root!r})"


    def add_document(self, *, key, document):
        path = os.path.join(self._root, key + ".html")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as stream:
            stream.write(document)


    def add_scalar(self, *, key, value, index=None, timestamp=None, marker=None):
        if timestamp is None:
            timestamp = arrow.utcnow().timestamp()
        if marker is None:
            marker = ""

        path = os.path.join(self._root, key + ".csv")

        if key not in self._keys:
            self._keys[key] = itertools.count()
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as stream:
                stream.write("index,timestamp,value,marker\n")

        if index is None:
            index = next(self._keys[key])

        with open(path, "a") as stream:
            stream.write(f"{index},{timestamp},{value},{marker}\n")

