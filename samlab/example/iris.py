# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Create example data and models based on the Iris dataset."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import gridfs
import pymongo

import samlab.observation
import samlab.serialize
import samlab.trial

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

    # Load the iris dataset using scikit-learn.
    import sklearn.datasets
    data = sklearn.datasets.load_iris()
    X = data["data"]
    Y = data["target"]
    feature_labels = data["feature_names"]
    class_labels = data["target_names"]

    # Create a database record for each observation.  Writing the features as
    # both contents and attributes is redundant, we do it here just to
    # demonstrate flexibility.
    for x, y in zip(X, Y):
        attributes = dict(zip(feature_labels, x))
        content = {
            "features": samlab.serialize.array(x),
            "label": samlab.serialize.array(y),
        }
        tags = ["label:%s" % class_labels[y]]
        samlab.observation.create(database, fs, attributes=attributes, content=content, tags=tags)


    # Create a trial object that will contain a description of the data.
    content = {
        "description": samlab.serialize.string(data["DESCR"]),
    }
    tags = ["label:overview"]
    samlab.trial.create(database, fs, name="Iris dataset overview", content=content)

    # Even though we already have the full dataset in memory, pretend that we
    # don't and load it from the database.
