# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import functools

import bson.objectid
import gridfs
import huey
import numpy
import pymongo

import samlab.database
import samlab.deserialize
import samlab.image
import samlab.model
import samlab.object
import samlab.observation
import samlab.plot

queue = huey.RedisHuey()


@functools.lru_cache(maxsize=None)
def get_database_client(uri):
    return pymongo.MongoClient(uri)


@functools.lru_cache(maxsize=None)
def get_database(uri, name):
    client = get_database_client(uri)
    database = client[name]
    fs = gridfs.GridFS(database)
    return database, fs


@functools.lru_cache(maxsize=1)
def get_model(database_uri, database_name, otype, oid, key):
    database, fs = get_database(database_uri, database_name)
    owner = database[otype].find_one({"_id": bson.objectid.ObjectId(oid)})

    assert(owner)
    assert(key in owner["content"])
    assert(owner["content"][key]["content-type"] == "application/x-keras-model")

    model = samlab.deserialize.keras_model(fs, owner["content"][key])
    return model


class Queue(object):
    def __init__(self, name):
        def get_model_summary_impl(database_uri, database_name, otype, oid, key):
            model = get_model(database_uri, database_name, otype, oid, key)
            summary = {
                "layers": [{"name": layer.name, "class_name": layer.__class__.__name__, "output_shape": layer.output_shape, "count_params": layer.count_params(), "config": layer.get_config()} for layer in model.layers],
                }
            return summary

        def get_model_layer_filter_gradient_ascent_impl(database_uri, database_name, otype, oid, key, layer, filter):
            model = get_model(database_uri, database_name, otype, oid, key)
            layer = model.get_layer(name=layer)
            image, losses = samlab.plot.gradient_ascent(model.input, layer, filter, 224, 224)
            return image

        def get_model_evaluate_images_impl(database_uri, database_name, mid):
            database, fs = get_database(database_uri, database_name)
            mid = bson.objectid.ObjectId(mid)

            model = database.models.find_one({"_id": mid})
            observations = samlab.observation.expand(database, samlab.deserialize.array(fs, model["content"]["observations"]))
            outputs = samlab.deserialize.array(fs, model["content"]["outputs"])[:len(observations)]

            # Check for previously-cached predictions
            if "cache:predictions" in model["content"]:
                predictions = samlab.deserialize.array(fs, model["content"]["cache:predictions"])
                count = len(predictions)

            else:
                batch_size = model["attributes"]["parameters"]["batch-size"]
                image_key = model["attributes"]["parameters"]["image-key"]

                keras_model = samlab.deserialize.keras_model(fs, model["content"]["model"])

                inputs = numpy.array([None] * len(observations))
                weights = numpy.ones_like(observations)

                batches = int(numpy.ceil(len(observations) / batch_size))
                count = batches * batch_size

                indices = numpy.arange(len(observations))

                data = samlab.observation.stream(observations, inputs, outputs, weights, indices)
                data = samlab.image.load(data, database, key=image_key)
                data = samlab.image.to_array(data)
                data = samlab.observation.batch(data, batch_size=batch_size, total_size=len(observations))

                predictions = keras_model.predict_generator(data, batches, verbose=1)

                samlab.object.set_content(database, fs, "models", mid, "cache:predictions", samlab.serialize.array(predictions))

            matches = numpy.equal(predictions[:count] > 0.5, outputs[:count])
            matches = numpy.all(matches, axis=1)

            return {"observations": observations[:count], "outputs": outputs[:count], "predictions": predictions[:count], "matches": matches[:count]}

        self._queue = huey.RedisHuey(name)
        self.get_model_summary = huey.api.TaskWrapper(self._queue, get_model_summary_impl)
        self.get_model_layer_filter_gradient_ascent = huey.api.TaskWrapper(self._queue, get_model_layer_filter_gradient_ascent_impl)
        self.get_model_evaluate_images = huey.api.TaskWrapper(self._queue, get_model_evaluate_images_impl)

    @property
    def queue(self):
        return self._queue


