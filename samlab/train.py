# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Utilities to simplify training artifacts."""

import logging

import numpy

log = logging.getLogger(__name__)


def random_split(dataset, split=0.1):
    """Return indices that randomly partition a dataset into two sets."""
    indices = numpy.random.choice(len(dataset), size=len(dataset), replace=False)
    boundary = int(len(indices) * split)
    return indices[boundary:], indices[:boundary]


def train_validate_test_split(dataset, test=0.2, validation=0.2):
    """Return indices that randomly partition a dataset into training, validation, and test sets."""
    indices = numpy.random.choice(len(dataset), size=len(dataset), replace=False)
    boundary = int(len(indices) * test)
    remaining_indices, test_indices = indices[boundary:], indices[:boundary]
    boundary = int(len(remaining_indices) * validation)
    training_indices, validation_indices = remaining_indices[boundary:], remaining_indices[:boundary]
    return training_indices, validation_indices, test_indices


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
                return results

    return results


class Loss:
    """Keeps track of whether a loss value has improved.
    """
    def __init__(self, delta=0):
        self._delta = delta
        self._loss = None

    def improved(self, loss):
        if self._loss is None:
            self._loss = loss
            return True
        if loss < self._loss - self._delta:
            self._loss = loss
            return True
        return False

    @property
    def value(self):
        return self._loss


class EarlyStop:
    """Stop training if a loss doesn't improve within N iterations.

    Parameters
    ----------
    patience: integer, optional
    """
    def __init__(self, patience=10, delta=0):
        self._patience = patience
        self._improved = Loss(delta=delta)

        self._count = 0
        self._total = 0
        self._triggered = False

    def __call__(self, loss):
        if self._triggered:
            return self._triggered

        self._total += 1

        if self._improved(loss):
            self._count = 0
        else:
            self._count += 1
            if self._count >= self._patience:
                self._triggered = True
                log.info(f"Early stop after {self._total} iterations.")
                log.info(f"Loss did not decrease beyond {self._improved.loss} in {self._patience} iterations.")
        return self._triggered

    @property
    def triggered(self):
        return self._triggered
