# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Tools for managing machine learning experiments."""

__version__ = "0.1.0"

import logging
import warnings

import arrow

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DeprecationWarning(Warning):
    pass


def deprecated(message):
    warnings.warn(message, DeprecationWarning, stacklevel=3)


class ElapsedTime(object):
    """Track elapsed time."""
    def __init__(self):
        self.reset()

    @property
    def start(self):
        """Return the start time / last reset time.

        Returns
        -------
        time: :class:`arrow.arrow.Arrow`
        """
        return self._start

    @property
    def elapsed(self):
        """Return elapsed time in seconds since the start time / last reset time.

        Returns
        -------
        seconds: float
        """
        return (arrow.utcnow() - self._start).total_seconds()

    def reset(self):
        """Reset the timer to zero."""
        self._start = arrow.utcnow()


class Progress(object):
    """Log progress messages during long running operations."""
    def __init__(self, step_message, log, total=None, finish_message=None, interval=5):
        if finish_message is None:
            finish_message = step_message

        self._total = total
        self._step_message = step_message
        self._finish_message = finish_message
        self._log = log
        self._interval = interval

        self._count = 0
        self._total_time = ElapsedTime()
        self._current_time = ElapsedTime()

    def step(self):
        self._count += 1
        if self._current_time.elapsed > self._interval:
            self._log.info(self._step_message.format(total=self._total, count=self._count, elapsed=self._total_time.elapsed, rate=self._count / self._total_time.elapsed))
            self._current_time.reset()

    def finish(self):
        self._log.info(self._finish_message.format(total=self._total, count=self._count, elapsed=self._total_time.elapsed, rate=self._count / self._total_time.elapsed))

