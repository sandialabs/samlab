# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Create example data and models based on the Iris dataset."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import gridfs
import pymongo

import samlab.observation

log = logging.getLogger(__name__)


def create(database, fs):
    """Add the iris dataset to an existing :ref:`database <database>`.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    fs: :class:`gridfs.GridFS` returned by :func:`samlab.database.connect`, required
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))

    import sklearn.datasets

    data = sklearn.datasets.load_iris()
    X = data["data"]
    feature_labels = data["feature_names"]
    Y = data["target"]
    class_labels = data["target_names"]

    for x, y in zip(X, Y):
        features = {key: value for key, value in zip(feature_labels, x)}
        tags = ["label:%s" % class_labels[y]]
        samlab.observation.create(database, fs, attributes=features, tags=tags)


