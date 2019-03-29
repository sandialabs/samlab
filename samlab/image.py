# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with image data."""

from __future__ import division

__version__ = "0.1.0"

import logging

import gridfs
import numpy
import pymongo
import PIL.Image
import scipy.stats

import samlab
import samlab.deserialize
import samlab.stream


log = logging.getLogger(__name__)

# Hide annoying log messages when loading PNG images using Pillow.
logging.getLogger("PIL.PngImagePlugin").setLevel(logging.INFO)


def load(generator, database, key="original"):
    """Deprecated, use :func:`samlab.stream.image_load` instead."""
    samlab.deprecated("samlab.image.load() is deprecated, use samlab.stream.image_load() instead.")
    return samlab.stream.image_load(generator, database, key)


def to_array(generator, rescale=1.0 / 255.0):
    """Deprecated, use :func:`samlab.stream.image_to_array` instead."""
    samlab.deprecated("samlab.image.to_array() is deprecated, use samlab.stream.image_to_array() instead.")
    return samlab.stream.image_to_array(generator, rescale)


def random_window(generator, shape, count=1, inputs=True, outputs=False):
    """Deprecated, use :func:`samlab.stream.random_array_window` instead."""
    samlab.deprecated("samlab.image.random_window() is deprecated, use samlab.stream.random_array_window() instead.")
    return samlab.stream.random_array_window(generator, shape, count, inputs, outputs)


def window(generator, shape, stride=None):
    """Deprecated, use :func:`samlab.stream.array_window` instead."""
    samlab.deprecated("samlab.image.window() is deprecated, use samlab.stream.array_window() instead.")
    return samlab.stream.array_window(generator, shape, stride)


def transform(generator, transforms, resample=PIL.Image.BICUBIC):
    """Deprecated, use :func:`samlab.stream.image_transform` instead."""
    samlab.deprecated("samlab.image.transform() is deprecated, use samlab.stream.image_transform() instead.")
    return samlab.stream.image_transform(generator, transforms, resample)


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

