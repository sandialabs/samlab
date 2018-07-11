# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with streaming data."""

from __future__ import division

__version__ = "0.1.0"

import logging

import tensorflow.contrib.keras as keras
import gridfs
import numpy
import pymongo
import PIL.Image

import samlab.deserialize


log = logging.getLogger(__name__)

# Hide annoying log messages when loading PNG images using Pillow.
logging.getLogger("PIL.PngImagePlugin").setLevel(logging.INFO)


def array_window(generator, shape, stride=None, inputs=True, outputs=False):
    """Extract subsets of images from :ref:`streaming-data` using a sliding window.

    Parameters
    ----------
    generator: generator expression, required
        Generator expression that produces (observation, input, output, weight) tuples.
    shape: (height, width) tuple, required
        Defines the size of the window to extract from incoming images.
    stride: (dy, dx) tuple, optional
        Defines the distance that the window moves between iterations.  By default, the
        window moves by `width` and `height` so that there is no overlap.
    inputs: bool, optional
        If True, window incoming inputs.  Assumes the input is a :class:`numpy.ndarray` with at least two dimensions.
    outputs: bool, optional
        If True, window incoming outputs.  Assumes the output is a :class:`numpy.ndarray` with at least two dimensions.

    Yields
    ------
    datum: tuple
        Yields multiple (observation, input, output, weight) tuples with `input` replaced by and instance of :class:`numpy.ndarray` with shape (height, width, 3).
    """
    height, width = shape

    if stride is None:
        stride = shape
    dy, dx = stride

    for observation, input, output, weight in generator:
        x = numpy.arange(0, input.shape[1] - width + 1, dx)
        y = numpy.arange(0, input.shape[0] - height + 1, dy)

        if x[-1] + width < input.shape[1]:
            x = numpy.append(x, [input.shape[1] - width])
        if y[-1] + height < input.shape[0]:
            y = numpy.append(y, [input.shape[0] - height])

        for iy in y:
            for ix in x:
                winput = input[iy: iy+height, ix: ix+width] if inputs else input
                woutput = output[iy: iy+height, ix: ix+width] if outputs else output
                yield observation, winput, woutput, weight


def batch(generator, batch_size, total_size, include_observations=False):
    """Group :ref:`streaming-data` into batches.

    Some modern machine learning algorithms (such as neural networks) train
    best when they receive batches of training datums instead of individual
    datums.  Use this function to group :ref:`streaming-data` into batches for
    ingestion by such algorithms.

    Parameters
    ----------
    generator: generator expression, required
        Generator expression that produces (observation, input, output, weight) tuples.
    batch_size: int, required
        Desired output batch size.
    total_size: int, required
        Total number of unique observations in the input.
    include_observations: bool, optional
        By default

    Yields
    ------
    datum: tuple
        Generates (input, output, weight) tuples where each element is an array
        of `batch-size` values, unless `include_observations` is True, in which
        case (observation, input, output, weight) tuples are generated.
    """
    count = 0
    observations = []
    inputs = []
    outputs = []
    weights = []
    while True:
        observation, input, output, weight = next(generator)
        observations.append(observation)
        inputs.append(input)
        outputs.append(output)
        weights.append(weight)
        count += 1

        if (len(observations) == batch_size) or (count == total_size):
            if include_observations:
                batch = (numpy.stack(observations), numpy.stack(inputs), numpy.stack(outputs), numpy.stack(weights))
            else:
                try:
                    batch = (numpy.stack(inputs), numpy.stack(outputs), numpy.stack(weights))
                except:
                    print([numpy.array(input).shape for input in inputs])
            observations = []
            inputs = []
            outputs = []
            weights = []
            if count == total_size:
                count = 0
            yield batch


def constant(observation, input, output, weight, repeat=1):
    """Turn a single observation into :ref:`streaming-data`.

    Parameters
    ----------
    observation, input, output, weight: anything, required
    repeat: int, optional
        The number of (observation, input, output, weight) tuples that should be generated.

    Yields
    ------
    datum: tuple
        Generates (observation, input, output, weight) tuples.
    """
    for index in numpy.arange(repeat):
        yield observation, input, output, weight


def image_load(generator, database, key="original"):
    """Load images from observations in :ref:`streaming-data`.

    Parameters
    ----------
    generator: generator expression, required
        Generator expression that produces (observation, input, output, weight) tuples.
    database: database object returned by :func:`samlab.database.connect`, required
    key: str, optional
        Observation content to be loaded.  Typically this will be "original"
        to load the original image, or some other key to load images that have
        been resized to a common size for fixed-length inputs.

    Yields
    ------
    datum: tuple
        Yields (observation, input, output, weight) tuples with `input` replaced by an instance of :class:`PIL.Image.Image`.
    """
    assert(isinstance(database, pymongo.database.Database))

    fs = gridfs.GridFS(database)

    cache = {}
    for observation, input, output, weight in generator:
        id = observation["_id"]
        if id not in cache:
            cache[id] = samlab.deserialize.image(fs, observation["content"][key])
        yield observation, cache[id], output, weight


#def image_resize(generator, size):
#    """Resize PIL images to the given size.
#
#    Parameters
#    ----------
#    size: (int, int) tuple.
#        Resize images to the given width and height.
#    """
#    target_width, target_height = size
#    for image, label, weight in generator:
#        image = image.resize((target_width, target_height), resample=PIL.Image.BICUBIC)
#        yield image, label, weight


def image_to_array(generator, rescale=1.0 / 255.0):
    """Convert images to feature vectors in :ref:`streaming-data`.

    Note
    ----
    Assumes that incoming data contains :class:`PIL.Image.Image` as the `input` for each datum.
    Grayscale images are converted to RGB images with identical channels.

    Parameters
    ----------
    generator: generator expression, required
        Generator expression that produces (observation, input, output, weight) tuples.
    rescale: float, optional
        Scaling value applied to image pixel values.  The default scales pixel values from [0, 255] to [0, 1].

    Yields
    ------
    datum: tuple
        Yields (observation, input, output, weight) tuples with `input` replaced by an instance of :class:`numpy.ndarray` with shape (height, width, 3).
    """
    for observation, image, output, weight in generator:
        image = keras.preprocessing.image.img_to_array(image) * rescale
        if image.shape[2] == 1:
            image = numpy.tile(image, (1, 1, 3))
        yield observation, image, output, weight


def image_transform(generator, transforms, resample=PIL.Image.BICUBIC):
    """Apply affine transformations to images in :ref:`streaming-data`.

    Note
    ----
    Assumes that incoming data contains :class:`PIL.Image.Image` as the `input` for each datum.

    Parameters
    ----------
    generator: generator expression, required
        Generator expression that produces (observation, input, output, weight) tuples.
    transforms: list of tuples, required
        List of affine transformations to be applied to each image, in order.  Each transform can be one-of:

        * ("random-horizontal-flip",)
        * ("random-vertical-flip",)
        * ("random-rotation", angle)
        * ("random-scale", minimum, maximum)
        * ("random-shear", amount)

    resample: resampling quality, optional

    Yields
    ------
    datum: tuple
        Yields (observation, input, output, weight) tuples with `input` replaced by a transformed image.
    """
    def identity():
        return numpy.identity(3)

    def rotate(theta):
        theta = numpy.deg2rad(theta)
        return numpy.array([[ numpy.cos(theta), numpy.sin(theta), 0],
                            [-numpy.sin(theta),  numpy.cos(theta), 0],
                            [0,                 0,                1]])

    def scale(w, h):
        return numpy.array([[w, 0, 0],
                            [0, h, 0],
                            [0, 0, 1]])

    def shear(x, y):
        return numpy.array([[1, x, 0],
                            [y, 1, 0],
                            [0, 0, 1]])

    def translate(x, y):
        return numpy.array([[1, 0, x],
                            [0, 1, y],
                            [0, 0, 1]])

    for observation, image, output, weight in generator:
        cx = image.size[0] / 2
        cy = image.size[1] / 2
        matrix = identity()
        matrix = matrix.dot(translate(cx, cy))
        for transform in transforms[::-1]:
            if transform[0] == "random-horizontal-flip":
                if numpy.random.random() < 0.5:
                    matrix = matrix.dot(scale(-1, 1))
            elif transform[0] == "random-vertical-flip":
                if numpy.random.random() < 0.5:
                    matrix = matrix.dot(scale(1, -1))
            elif transform[0] == "random-rotation":
                matrix = matrix.dot(rotate(numpy.random.uniform(0, transform[1])))
            elif transform[0] == "random-scale":
                matrix = matrix.dot(scale(numpy.random.uniform(transform[1], transform[2]), numpy.random.uniform(transform[1], transform[2])))
            elif transform[0] == "random-shear":
                matrix = matrix.dot(shear(numpy.random.uniform(-transform[1], transform[1]), numpy.random.uniform(-transform[1], transform[1])))
            else:
                raise ValueError("Unknown transformation: %s" % transform)
        matrix = matrix.dot(translate(-cx, -cy))

        image = image.transform(image.size, PIL.Image.AFFINE, data=numpy.linalg.inv(matrix)[0:2].flatten(), resample=resample)
        yield observation, image, output, weight


#def isotropic_image_resize(generator, size):
#    """Resize images isotropically.
#
#    Parameters
#    ----------
#    size: int.
#        Resize images isotropically so the shortest side matches the given size.
#    """
#    for image, label in generator:
#        if image.width > image.height:
#            target_width = int(float(image.width) / float(image.height) * size)
#            target_height = size
#        else:
#            target_width = size
#            target_height = int(float(image.height) / float(image.width) * size)
#        image = image.resize((target_width, target_height), resample=PIL.Image.BICUBIC)
#        yield image, label


def random_array_window(generator, shape, count=1, inputs=True, outputs=False):
    """Extract subsets of images from :ref:`streaming-data` using a random window.

    Parameters
    ----------
    generator: generator expression, required
        Generator expression that produces (observation, input, output, weight) tuples.
    shape: (height, width) tuple, required
        Defines the size of the window to extract from incoming images.
    count: int, optional
        The number of randomly-chosen windows to return from a single observation.
    inputs: bool, optional
        If True, window incoming inputs.  Assumes the input is a :class:`numpy.ndarray` with at least two dimensions.
    outputs: bool, optional
        If True, window incoming outputs.  Assumes the output is a :class:`numpy.ndarray` with at least two dimensions.

    Yields
    ------
    datum: tuple
        Yields `count` (observation, input, output, weight) tuples with windowed inputs and/or outputs.
    """
    height, width = shape

    for observation, input, output, weight in generator:
        for index in numpy.arange(count):
            oshape = None
            if inputs:
                oshape = input.shape
            if outputs:
                oshape = output.shape

            ix = numpy.random.choice(oshape[1] - width)
            iy = numpy.random.choice(oshape[0] - height)
            #log.debug("window: %s: %s, %s: %s", iy, iy+height, ix, ix+width)
            winput = input[iy: iy+height, ix: ix+width] if inputs else input
            woutput = output[iy: iy+height, ix: ix+width] if outputs else output

            yield observation, winput, woutput, weight



