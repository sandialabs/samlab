# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with image data."""

from __future__ import division

__version__ = "0.1.0"

import logging

import numpy
import scipy.stats


log = logging.getLogger(__name__)


def density_map(size, points, covariance=None):
    """Compute a 2D density map by mixing gaussians.

    Parameters
    ----------
    size: tuple, required
        Output image (width, height) tuple.
    points: 2D array of point coordinates, required
    covarance: number, sequence of numbers, 2x2 matrix, or sequence of 2x2 matrices, optional

    Returns
    -------
    density: :class:`numpy.ndarray`
        Numpy array with shape `size`.
    """

    size = numpy.asarray(size)
    assert(size.ndim == 1)
    assert(size.shape[0] == 2)

    points = numpy.asarray(points)
    assert(points.ndim == 2)
    assert(points.shape[1] == 2)

    if covariance is None:
        covariance = 1
    covariance = numpy.asarray(covariance)
    if covariance.ndim == 0:
        covariance = numpy.array([[covariance, 0], [0, covariance]])
    if covariance.ndim == 1:
        covariance = numpy.array([[[cov, 0], [0, cov]] for cov in covariance])
    if covariance.ndim == 2:
        covariance = numpy.tile(covariance, (len(points), 1, 1))
    assert(covariance.ndim == 3)
    assert(covariance.shape[0] == points.shape[0])
    assert(covariance.shape[1] == 2)
    assert(covariance.shape[2] == 2)

    coordinates = numpy.dstack(numpy.meshgrid(numpy.arange(size[0]), numpy.arange(size[1]), indexing="xy"))
    density = numpy.zeros((size[1], size[0]), dtype="float")

    for point, cov in zip(points, covariance):
        gaussian = scipy.stats.multivariate_normal(mean=point, cov=cov)
        pdensity = gaussian.pdf(coordinates)
        density += pdensity

    return density

