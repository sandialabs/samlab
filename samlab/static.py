# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with :ref:`static-data`."""

from __future__ import absolute_import, division, print_function, unicode_literals

import collections
import copy
import io
import logging

import arrow
import bson
import gridfs
import numpy
import pymongo
import six

import samlab
import samlab.deserialize
import samlab.search
import samlab.serialize

log = logging.getLogger(__name__)


def load(database, filter=None):
    """Load static data from the :ref:`database`.

    Returns :ref:`static-data` containing empty inputs and outputs and a
    weight of 1.0 for each observation.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    filter: filter specification compatible with `pymongo.collection.Collection.find`, optional

    Returns
    -------
    observations: :class:`numpy.ndarray`
        Returned observations
    inputs: :class:`numpy.ndarray`
        A `None` value for each observation.
    outputs: :class:`numpy.ndarray`
        A `None` value for each observation.
    weights: :class:`numpy.ndarray`
        A weight of 1.0 for each observation.
    """

    assert(isinstance(database, pymongo.database.Database))

    cursor = database.observations.find(filter=filter)
    log.info("Loading %s observations.", cursor.count())

    observations = []
    inputs = []
    outputs = []
    weights = []

    for observation in cursor:
        observations.append(observation)
        inputs.append(None)
        outputs.append(None)
        weights.append(1.0)

    observations = numpy.array(observations)
    inputs = numpy.array(inputs)
    outputs = numpy.array(outputs)
    weights = numpy.array(weights)

    return observations, inputs, outputs, weights


def map(observations, inputs, outputs, weights, mapper):
    """Used to extract inputs, outputs, and weights from :ref:`static-data`.

    This function allows callers to apply a `mapper` to each datum in a set of
    :ref:`static-data`, optionally modifying the data as it goes.  The mapper
    must be a function that takes `observation`, `input`, `output`, and
    `weight` arguments, returning (optionally modified) values for `input`,
    `output`, and `weight`.  Since the mapper could return its input values
    unchanged, mappers can be used to generate any combination of input,
    output, and weight data.  Typically, mappers will examine the contents of
    each observation in order to extract an input feature vector, output
    feature vector, or weight.

    Parameters
    ----------
    observations: :class:`numpy.ndarray`, required
    inputs: :class:`numpy.ndarray`, required
    outputs: :class:`numpy.ndarray`, required
    weights: :class:`numpy.ndarray`, required
    mapper: mapping function, required

    Returns
    -------
    observations: :class:`numpy.ndarray`
        Same as the input `observations`.
    inputs: :class:`numpy.ndarray`
        Modified input values.
    outputs: :class:`numpy.ndarray`
        Modified output values.
    weights: :class:`numpy.ndarray`
        Modified weight values.
    """
    assert(len(observations) == len(inputs))
    assert(len(observations) == len(outputs))
    assert(len(observations) == len(weights))

    new_inputs = []
    new_outputs = []
    new_weights = []
    for observation, input, output, weight in zip(observations, inputs, outputs, weights):
        input, output, weight = mapper(observation, input, output, weight)
        new_inputs.append(input)
        new_outputs.append(output)
        new_weights.append(weight)
    new_inputs = numpy.array(new_inputs)
    new_outputs = numpy.array(new_outputs)
    new_weights = numpy.array(new_weights)

    return observations, new_inputs, new_outputs, new_weights


def log_outputs(observations, inputs, outputs, weights, names):
    """Log information about :ref:`static-data`.

    Given a set of :ref:`static-data`, logs information about
    the number of observations and the number of unique output
    values (i.e. the number of classes in a classification problem).

    Parameters
    ----------
    observations: :class:`numpy.ndarray`, required
    inputs: :class:`numpy.ndarray`, required
    outputs: :class:`numpy.ndarray`, required
    weights: :class:`numpy.ndarray`, required

    Returns
    -------
    observations: :class:`numpy.ndarray`
        Same as the input `observations`.
    inputs: :class:`numpy.ndarray`
        Modified input values.
    outputs: :class:`numpy.ndarray`
        Modified output values.
    weights: :class:`numpy.ndarray`
        Modified weight values.
    """

    assert(len(observations) == len(inputs))
    assert(len(observations) == len(outputs))
    assert(len(observations) == len(weights))

    names = {key: value for key, value in names}

    log.info("Identified %s unique outputs in %s observations:", len(numpy.unique(outputs)), len(outputs))
    for output in numpy.unique(outputs, axis=0):
        selection = numpy.equal(outputs, output).all(axis=1)
        count = numpy.count_nonzero(selection)
        log.info("  Output %s (%s) count: %s (%.2f%%)", output, names[tuple(output)], count, count / len(outputs) * 100.0)
    return observations, inputs, outputs, weights


#def label_weights(paths, labels, weights, method="unary"):
#    if method == "unary":
#        weights = numpy.ones_like(paths, dtype="double")
#    elif method == "idf":
#        for label in numpy.unique(labels):
#            selection = (labels == label)
#            count = numpy.count_nonzero(selection)
#            weights[selection] = numpy.log(len(paths) / (count + 1))
#    else:
#        raise ValueError("Unknown method: %s" % method)
#
#    return paths, labels, weights


def stream(observations, inputs, outputs, weights, indices=None, repeat=True):
    """Convert :ref:`static-data` into :ref:`streaming-data`

    Parameters
    ----------
    observations: :class:`numpy.ndarray`, required
    inputs: :class:`numpy.ndarray`, required
    outputs: :class:`numpy.ndarray`, required
    weights: :class:`numpy.ndarray`, required
    indices: :class:`numpy.ndarray`, optional
        Specifies a subset of the input data to be converted to streaming
        output.  By default, all input data will be streamed as output.
        Typically, this would be an index array returned by a :ref:`partition
        generator <partition-generators>`.
    repeat: bool, optional
        If `True`, this function will repeat its inputs forever, so it is up
        to the consumer to stop iteration.  This behavior is the default since
        it is typical to want to iterate over the input data for many epochs
        during training.

    Yields
    ------
    datum: tuple
        Yields (observation, input, output, weight) tuples.
    """

    assert(len(observations) == len(inputs))
    assert(len(observations) == len(outputs))
    assert(len(observations) == len(weights))

    if indices is None:
        indices = numpy.arange(len(observations))

    while True:
        for index in indices:
            yield observations[index], inputs[index], outputs[index], weights[index]
        if not repeat:
            break


