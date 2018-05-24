# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with :ref:`models`."""

from __future__ import absolute_import, division, print_function, unicode_literals

import collections
import logging
import os
import tempfile

import arrow
import bson.objectid
import gridfs
import numpy
import pymongo
import six
import tensorflow
import tensorflow.contrib.keras as keras

import samlab


log = logging.getLogger(__name__)


def create(database, fs, trial, name, attributes=None, content=None, tags=None):
    """Add a new model to the :ref:`database <database>`.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    fs: :class:`gridfs.GridFS`, required
    trial: :class:`bson.objectid.ObjectId`, required
        ID of the trial that will own this model.
    name: string, required
        Human-readable model name.
    attributes: dict, optional
        Optional metadata to be stored with this model.  Be sure to pass this
        data through :func:`samlab.serialize.attributes` to ensure that it only
        contains types that can be stored in the database.
    content: dict, optional
        Dict containing content to be stored for this model.  The value for
        each key-value pair in the content should be created using functions in
        :mod:`samlab.serialize`.
    tags: list of str, optional
        Tags to be stored with this model.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(trial, bson.objectid.ObjectId))
    assert(isinstance(name, six.string_types))

    if attributes is None:
        attributes = {}
    assert(isinstance(attributes, dict))

    if content is None:
        content = {}
    assert(isinstance(content, dict))
    content = {role: {"data": fs.put(spec["data"]), "content-type": spec["content-type"], "filename": spec.get("filename", None)} for role, spec in content.items()}

    if tags is None:
        tags = []
    assert(isinstance(tags, list))
    for tag in tags:
        assert(isinstance(tag, six.string_types))

    document = {
        "attributes": attributes,
        "content": content,
        "created": arrow.utcnow().datetime,
        "name": name,
        "tags": tags,
        "trial": trial,
    }

    database.models.create_index("tags")
    database.models.create_index([("$**", pymongo.TEXT)])
    return database.models.insert_one(document).inserted_id


def delete(database, fs, mid):
    """Delete a model from the :ref:`database <database>`.

    Note that this implicitly deletes any data owned by the model.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    fs: :class:`gridfs.GridFS`, required
    mid: :class:`bson.objectid.ObjectId`, required
        Unique database identifier for the model to be deleted.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(fs, gridfs.GridFS))
    assert(isinstance(mid, bson.objectid.ObjectId))

    # Delete favorites pointing to this model
    database.favorites.delete_many({"otype": "models", "oid": str(mid)})
    # Delete content owned by this model
    for model in database.models.find({"_id": mid}):
        for key, value in model["content"].items():
            fs.delete(value["data"])
    # Delete the model
    database.models.delete_many({"_id": mid})


def set_content(database, model, role, new_content):
    """Deprecated, use :func:`samlab.object.set_content` instead."""
    samlab.deprecated("samlab.model.set_content() is deprecated, use samlab.object.set_content() instead.")

    fs = gridfs.GridFS(database)

    import samlab.object
    samlab.object.set_content(database, fs, model["_id"], role, new_content)


def fine_tune_vgg16(parameters, training_data, validation_data, test_data, training_count, validation_count, test_count):
    """Train a CNN model by fine-tuning VGG-16 trained on ImageNet.

    Parameters
    ----------
    parameters: dict, required
        Dict containing hyperparameters needed by this model:

        * batch-size
        * dropout
        * fc1
        * fc2
        * fine-tuning-layers
        * image-size
        * optimizer
        * reduce-learning-rate

    training_data: generator expression, required
        Generator expression that yields (observation, input, output, weight) tuples.
    validation_data: generator expression, required
        Generator expression that yields (observation, input, output, weight) tuples.
    test_data: generator expression, required
        Generator expression that yields (observation, input, output, weight) tuples.
    training_count: int, required
        Number of training observations to use during one epoch
    validation_count: int, required
        Number of validation observations to use during one epoch
    test_count: int, required
        Number of test observations to use during one epoch

    Returns
    -------
    results: dict
        Dictionary containing training results:

        * model-path
        * test-accuracies
        * test-losses
        * training-accuracies
        * training-losses
        * validation-accuracies
        * validation-losses
    """
    log.info("Using tensorflow %s", tensorflow.__version__)

    # We don't want Keras/Tensorflow to preallocate the entire GPU
    config = tensorflow.ConfigProto(gpu_options=tensorflow.GPUOptions(per_process_gpu_memory_fraction=0, allow_growth=True))
    session = tensorflow.Session(config=config)
    keras.backend.set_session(session)

    # Load an existing network trained on VGG-16, but leave-out the classification layers.
    original = keras.applications.vgg16.VGG16(weights="imagenet", include_top=False, input_shape=(parameters["image-size"], parameters["image-size"], 3))

    # By default, we won't train any of the convolutional layers provided by VGG-16.
    for layer in original.layers:
        layer.trainable = False

    # However, we will allow (optional) fine-tuning of weights in later layers.
    if parameters["fine-tuning-layers"]:
        for layer in original.layers[-parameters["fine-tuning-layers"] : ]:
            layer.trainable = True

    # Attach our own classfication layers to the VGG16 convolution layers.
    model = original.output
    model = keras.layers.Flatten()(model)

    if parameters["fc1"]["shape"]:
        model = keras.layers.Dense(parameters["fc1"]["shape"], name="fc1")(model)
        model = keras.layers.Activation("relu", name="fc1_activation")(model)
        if parameters["fc1"]["batch-normalization"]:
            model = keras.layers.BatchNormalization(name="fc1_batch_normalization")(model)
        model = keras.layers.Dropout(parameters["dropout"], name="fc1_dropout")(model)

    if parameters["fc2"]["shape"]:
        model = keras.layers.Dense(parameters["fc2"]["shape"], name="fc2")(model)
        model = keras.layers.Activation("relu", name="fc2_activation")(model)
        if parameters["fc2"]["batch-normalization"]:
            model = keras.layers.BatchNormalization(name="fc2_batch_normalization")(model)
        model = keras.layers.Dropout(parameters["dropout"], name="fc2_dropout")(model)

    model = keras.layers.Dense(parameters["output"]["shape"], name="output")(model)
    model = keras.layers.Activation(parameters["output"]["activation"], name="output_activation")(model)
    model = keras.models.Model(inputs=original.input, outputs=model)

    # Setup optimization.
    opt_name, opt_params = parameters["optimizer"]
    if opt_name == "adam":
        optimizer = keras.optimizers.Adam(**opt_params)
    elif opt_name == "sgd":
        optimizer = keras.optimizers.SGD(**opt_params)
    else:
        raise ValueError("Unown optimizer: %s" % parameters["optimizer"])
    model.compile(loss=parameters["loss"], optimizer=optimizer, metrics=["accuracy"])

    # A helper to keep track of loss and accuracy as we train.
    class RecordMetrics(keras.callbacks.Callback):
        def __init__(self, data, batch_size, total_size):
            self._data = data
            self._steps = int(numpy.ceil(total_size / batch_size))
            self.history = collections.defaultdict(list)

        def on_epoch_end(self, epoch, logs={}):
            metrics = self.model.evaluate_generator(self._data, steps=self._steps)
            for name, metric in zip(self.model.metrics_names, metrics):
                self.history[name].append(metric)

    # Keep track of loss and accuracy history for our test data.
    test_metrics = RecordMetrics(test_data, batch_size=parameters["batch-size"], total_size=test_count)

    # Set aside a temporary path where we can checkpoint the model state.
    fd, model_path = tempfile.mkstemp(suffix=".hdf5")
    os.close(fd)

    callbacks = [
        test_metrics,
        keras.callbacks.EarlyStopping(monitor="val_loss", patience=20, verbose=1),
        keras.callbacks.ModelCheckpoint(model_path, monitor="val_loss", verbose=1, save_best_only=True)
    ]

    if parameters["reduce-learning-rate"]:
        callbacks.append(keras.callbacks.ReduceLROnPlateau(monitor="val_loss", patience=10, factor=0.3, verbose=1))

    history = model.fit_generator(
        training_data,
        steps_per_epoch=int(numpy.ceil(training_count / parameters["batch-size"])),
        epochs=parameters["epochs"],
        validation_data=validation_data,
        validation_steps=int(numpy.ceil(validation_count / parameters["batch-size"])),
        callbacks=callbacks,
        verbose=1,
    )

    training_losses = numpy.array(history.history["loss"])
    training_accuracies = numpy.array(history.history["acc"])
    validation_losses = numpy.array(history.history["val_loss"])
    validation_accuracies = numpy.array(history.history["val_acc"])
    test_losses = numpy.array(test_metrics.history["loss"])
    test_accuracies = numpy.array(test_metrics.history["acc"])

    results = {
        "model-path": model_path,
        "test-accuracies": test_accuracies,
        "test-losses": test_losses,
        "training-accuracies": training_accuracies,
        "training-losses": training_losses,
        "validation-accuracies": validation_accuracies,
        "validation-losses": validation_losses,
    }

    return results
