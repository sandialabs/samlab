# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import contextlib
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
    debug: bool, optional
        If :any:`True`, allow samlab server debugging.
    """
    def __init__(self, host=None, port=None, config=True, coverage=False, debug=False, quiet=True):
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
        if debug:
            command += ["--debug"]

        env = dict(os.environ)
        if coverage:
            env["SAMLAB_DASHBOARD_COVERAGE"] = "1"

        log.info("Starting dashboard server: %s", " ".join(command))
        self._server = subprocess.Popen(command, stdout=output, stderr=output)

        self._host = host
        self._port = port
        self._config = config
        self._coverage = coverage
        self._quiet = quiet
        self._debug = debug


    def __repr__(self):
        return "samlab.dashboard.Server(host={self._host!r}, port={self._port!r}, config={self._config!r}, coverage={self._coverage!r}, quiet={self._quiet!r}, debug={self._debug!r})"


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
                raise RuntimeError("Timed-out waiting for server.")

            try:
                requests.get(self.uri + "/ready", proxies={"http": None})
                return
            except Exception as e:
                print(e)
                time.sleep(1.0)


    def stop(self):
        """Stop the running dashboard server.
        Raises
        ------
        RuntimeError, if called more than once, or called on an instance used as a context manager.
        """
        if not self._server:
            raise RuntimeError("dashboard server already stopped.")

        log.info("Stopping dashboard server.")
        self._server.send_signal(signal.SIGINT)
        self._server.wait()
        self._server = None
        log.info("Dashboard server stopped.")


    @property
    def uri(self):
        """Address of the running server that can be used with web clients."""
        return "http://%s:%s" % (self._host, self._port)

