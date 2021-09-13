# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Utilities to simplify user interaction during experiments."""

import logging
import os
import signal
import time

import numpy
import tqdm.auto as tqdm

import samlab


log = logging.getLogger(__name__)


class Stop(object):
    """Handle interrupts so training can be interrupted gracefully.

    Create an instance of :class:`samlab.interactive.Stop` and check its
    `triggered` property periodically during training.  If `triggered`
    is `True` then the user has interrupted the process, either with
    CTRL-C or the Jupyter `Interrupt Kernel` button.
    """
    def __init__(self, timeout=5.0):
        self._pid = os.getpid()
        self._triggered = False
        self._trigger_time = None
        self._timeout = timeout
        signal.signal(signal.SIGINT, self._handler)

    def _log(self, message):
        # Don't repeat log messages in child processes.
        if self._pid != os.getpid():
            return
        log.info(message)

    def trigger(self):
        """Programmatically trigger an interruption."""
        now = time.time()
        if self._triggered and now - self._trigger_time < self._timeout:
            self._log("Interrupting.")
            raise KeyboardInterrupt()
        else:
            self._triggered = True
            self._trigger_time = now
            self._log(f"Received signal to stop. Trigger again within {self._timeout} seconds to interrupt process.")

    def _handler(self, signal, frame):
        self.trigger()

    @property
    def triggered(self):
        """`True` if the user has interrupted the process, `False` otherwise."""
        return self._triggered


class Progress(object):
    """Display a graphical progress bar while iterating over a sequence."""
    def __init__(self, desc=None, unit=None):
        import tqdm
        self._progress = tqdm.tqdm(desc=desc, unit=unit)

    def __call__(self, iterable, desc=None, unit=None):
        self._progress.reset(total=len(iterable))
        if desc is not None:
            self._progress.set_description(desc, refresh=False)
        if unit is not None:
            self._progress.unit = unit
        self._progress.refresh()

        for item in iterable:
            yield item

            self._progress.update(1)
            self._progress.refresh()

