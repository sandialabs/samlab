"""Utilities to simplify training models."""

import logging
import os
import signal

import numpy
import tqdm.auto as tqdm

log = logging.getLogger(__name__)


class Stop(object):
    """Handle interrupts gracefully so training can be interrupted.

    Create an instance of :class:`samlab.train.Stop` and check its
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


def k_fold(dataset, n=5, k=2, validation=0.2, count=None):
    """Return sets of indices partitioning a dataset for K-fold cross validation."""
    assert(k > 1)

    results = []
    for iteration in range(n):
        indices = numpy.random.choice(len(dataset), size=len(dataset), replace=False)
        folds = numpy.array_split(indices, k)

        for index, test_indices in enumerate(folds):
            remaining = numpy.concatenate(folds[:index] + folds[index+1:])
            boundary = int(len(remaining) * validation)
            validation_indices, training_indices = remaining[:boundary], remaining[boundary:]

            results.append((training_indices, validation_indices, test_indices))

            if count is not None and len(results) >= count:
                break

    return results


def progress(iterable, description, units, leave=True):
    """Wrap an iterable to produce progress output."""
    return tqdm.tqdm(iterable, leave=leave, desc=description, unit=units)


