# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Utilities to simplify training models."""

import logging

import numpy

log = logging.getLogger(__name__)


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


