# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Utilities to simplify user interaction during experiments."""

import logging
import os
import signal

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
    def __init__(self):
        self._pid = os.getpid()
        self._triggered = False
        signal.signal(signal.SIGINT, self._handler)

    def trigger(self):
        """Programmatically trigger an interruption."""
        if not self._triggered:
            self._triggered = True
            # Don't log the message in child processes
            if self._pid == os.getpid():
                log.info("Received signal to stop.")

    def _handler(self, signal, frame):
        self.trigger()

    @property
    def triggered(self):
        """`True` if the user has interrupted the process, `False` otherwise."""
        return self._triggered


def progress(iterable, description, unit, leave=True):
    """Wrap an iterable to produce progress output."""
    samlab.deprecated("samlab.interactive.progress() is deprecated, use the tqdm library directly instead.")
    return tqdm.tqdm(iterable, leave=leave, desc=description, unit=unit)


