# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for training new models.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import numpy
import sklearn.model_selection


log = logging.getLogger(__name__)


def log_parameters(parameters):
    """Log parameter values for information / debugging.

    Parameters
    ----------
    parameters: dict, required
        Dictionary of parameter values to be logged.
    """
    for key, value in sorted(parameters.items()):
        log.info("Hyperparameter %s: %s", key, value)


def log_partition(partition, outputs=None, output_names=None):
    """Log partitioning information for information / debugging.

    Parameters
    ----------
    partition: (label, training_indices, validation_indices, test_indices) tuple
        Partition returned by a :ref:`Partition Generator <partition-generators>`.
    outputs: :class:`numpy.ndarray`, optional
        Training :ref:`outputs`.
    output_names: dict, optional
        Mapping from unique output values to human-readable labels.
    """

    label, training_indices, validation_indices, test_indices = partition

    log.info("Partition %s:", label)
    for name, indices in [("training", training_indices), ("validation", validation_indices), ("test", test_indices)]:
        log.info("  Using %s %s observations.", len(indices), name)
        if outputs and output_names and len(outputs[indices]):
            for output in numpy.unique(outputs[indices], axis=0):
                selection = numpy.equal(outputs[indices], output).all(axis=1)
                count = numpy.count_nonzero(selection)
                log.info("    Output %s (%s) count: %s (%.2f%%)", output, output_names[tuple(output)], count, count / len(outputs[indices]) * 100.0)


def random(inputs, outputs, validation_split=0.2, test_split=0.5, n=1):
    """:ref:`Partition generator <partition-generators>` that creates random partitions.

    Splits data using random sampling, useful for regression problems.  The
    `test_split` parameter specifies the percentage of the original data to be
    held-back for testing.  The `validation_split` parameter specifieds the
    percentage of the remaining training data to be used for validation.  The
    process is repeated :math:`n` times, generating a total of :math:`n`
    partitions.

    Parameters
    ----------
    inputs, outputs: :ref:`static-data` input and output arrays, required
    validation_split: float, optional
    test_split: float, optional
    n: int, optional
        Specifies the number of partitions to generate.

    Yields
    ------
    label: string
    training_indices: :class:`numpy.ndarray`
    validation_indices: :class:`numpy.ndarray`
    test_indices: :class:`numpy.ndarray`
    """
    for index in range(n):
        if test_split:
            remaining, test_indices = next(sklearn.model_selection.ShuffleSplit(n_splits=1, test_size=test_split).split(inputs, outputs))
        else:
            remaining = numpy.arange(len(inputs))
            numpy.random.shuffle(remaining)
            test_indices = numpy.array([], dtype="int")

        if validation_split:
            training_indices, validation_indices = next(sklearn.model_selection.ShuffleSplit(n_splits=1, test_size=validation_split).split(inputs[remaining], outputs[remaining]))
        else:
            training_indices = remaining
            validation_indices = numpy.array([], dtype="int")
        yield "Random-%s" % index, training_indices, validation_indices, test_indices


def stratify(inputs, outputs, validation_split=0.2, test_split=0.5, n=1):
    """:ref:`Partition generator <partition-generators>` that creates stratified random partitions.

    Splits data using stratified sampling so that the proportion of output
    values in each partition is roughly equal to its proportion in the original
    :ref:`static-data`, useful for classification problems.  The `test_split`
    parameter specifies the percentage of the original data to be held-back for
    testing.  The `validation_split` parameter specifieds the percentage of the
    remaining training data to be used for validation.  The process is repeated
    :math:`n` times, generating a total of :math:`n` partitions.

    Parameters
    ----------
    inputs, outputs: :ref:`static-data` input and output arrays, required
    validation_split: float, optional
    test_split: float, optional
    n: int, optional
        Specifies the number of partitions to generate.

    Yields
    ------
    label: string
    training_indices: :class:`numpy.ndarray`
    validation_indices: :class:`numpy.ndarray`
    test_indices: :class:`numpy.ndarray`
    """
    for index in range(n):
        if test_split:
            remaining, test_indices = next(sklearn.model_selection.StratifiedShuffleSplit(n_splits=1, test_size=test_split).split(inputs, outputs))
        else:
            remaining = numpy.arange(len(inputs))
            numpy.random.shuffle(remaining)
            test_indices = numpy.array([], dtype="int")

        if validation_split:
            training_indices, validation_indices = next(sklearn.model_selection.StratifiedShuffleSplit(n_splits=1, test_size=validation_split).split(inputs[remaining], outputs[remaining]))
        else:
            training_indices = remaining
            validation_indices = numpy.array([], dtype="int")
        yield "Stratified-%s" % index, training_indices, validation_indices, test_indices


def k_fold(inputs, outputs, validation_split=0.2, n=5, k=2, stratified=True):
    """:ref:`Partition generator <partition-generators>` that creates partitions for k-fold cross-validation.

    Splits data using stratified sampling so that the proportion of output
    values in each partition is roughly equal to its proportion in the original
    :ref:`static-data`.

    The original data is randomly split into :math:`k` folds. One fold is held-back for testing,
    and the remaining :math:`k-1` folds are used for training, with `validation_split`
    used to hold-back a percentage training samples for validation.  This process is repeated
    :math:`k` times so that each fold is used once for testing and :math:`k-1` times for training.

    Then the entire process is repeated :math:`n` times, so that a total of :math:`n \\times k` partitions
    are returned.

    Parameters
    ----------
    inputs, outputs: :ref:`static-data` input and output arrays, required
    validation_split: float, optional
    n: int, optional
        Specifies the number of k-fold partitions to generate.
    k: int, optional
        Specifies the number of folds.  Currently, only 2 are allowed.

    Yields
    ------
    label: string
    training_indices: :class:`numpy.ndarray`
    validation_indices: :class:`numpy.ndarray`
    test_indices: :class:`numpy.ndarray`
    """
    if k != 2:
        raise NotImplementedError("Not implemented for k != 2.")

    for index in range(n):
        if stratified:
            a_indices, b_indices = next(sklearn.model_selection.StratifiedShuffleSplit(n_splits=1, test_size=0.5).split(inputs, outputs))
        else:
            a_indices, b_indices = next(sklearn.model_selection.ShuffleSplit(n_splits=1, test_size=0.5).split(inputs, outputs))

        test_indices = a_indices
        if stratified:
            training_indices, validation_indices = next(sklearn.model_selection.StratifiedShuffleSplit(n_splits=1, test_size=validation_split).split(inputs[b_indices], outputs[b_indices]))
        else:
            training_indices, validation_indices = next(sklearn.model_selection.ShuffleSplit(n_splits=1, test_size=validation_split).split(inputs[b_indices], outputs[b_indices]))
        yield "%s x %s cross validation %s-%s" % (n, k, index, 0), training_indices, validation_indices, test_indices

        test_indices = b_indices
        if stratified:
            training_indices, validation_indices = next(sklearn.model_selection.StratifiedShuffleSplit(n_splits=1, test_size=validation_split).split(inputs[a_indices], outputs[a_indices]))
        else:
            training_indices, validation_indices = next(sklearn.model_selection.ShuffleSplit(n_splits=1, test_size=validation_split).split(inputs[a_indices], outputs[a_indices]))
        yield "%s x %s cross validation %s-%s" % (n, k, index, 1), training_indices, validation_indices, test_indices


def mean_loss(losses):
    """Experimental."""
    # Calculate the min of each series of losses, skipping empty series.  Any series that contains NaN, will have a NaN minimum.
    losses = [numpy.amin(loss) for loss in losses if len(loss)]
    # Filter-out an NaNs.
    losses = [loss for loss in losses if not numpy.isnan(loss)]
    # Calculate the mean of the results (if any)
    loss = numpy.mean(losses) if len(losses) else None

    return loss
