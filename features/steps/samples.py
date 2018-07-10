# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

from behave import *

import logging

import nose.tools

import samlab.observation


@given(u'the iris dataset')
def step_impl(context):
    import sklearn.datasets
    data = sklearn.datasets.load_iris()
    X = data["data"]
    feature_labels = data["feature_names"]
    Y = data["target"]
    class_labels = data["target_names"]

    for x, y in zip(X, Y):
        features = {key: value for key, value in zip(feature_labels, x)}
        tags = ["label:%s" % class_labels[y]]
        samlab.observation.create(context.database, context.fs, attributes=features, tags=tags)

