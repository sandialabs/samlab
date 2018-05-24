# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import functools
import io
import logging
import os
import tempfile
import zipfile

log = logging.getLogger(__name__)

import gridfs
import huey
import numpy
import pymongo
import sklearn.cluster
import sklearn.preprocessing

import samlab.deserialize
import samlab.mime
import samlab.observation


@functools.lru_cache(maxsize=None)
def get_database_client(uri):
    return pymongo.MongoClient(uri)


@functools.lru_cache(maxsize=None)
def get_database(uri, name):
    client = get_database_client(uri)
    database = client[name]
    fs = gridfs.GridFS(database)
    return database, fs


class Queue(object):
    def __init__(self):
        def cluster_content_impl(database_uri, database_name, otype, content, preprocessor, algorithm):
            database, fs = get_database(database_uri, database_name)
            oids = []
            features = []
            for o in database[otype].find({"content.%s" % content : {"$exists": True}}):
                oids.append(o["_id"])
                features.append(o["content"][content])

            features = [samlab.deserialize.array(fs, f) for f in features]
            features = numpy.array(features)

            assert(features.ndim == 2)

            preprocessor_name = preprocessor["name"]
            if preprocessor_name == "minmax":
                normalized = sklearn.preprocessing.minmax_scale(features, feature_range=(0, 1))
            elif preprocessor_name == "scale":
                normalized = sklearn.preprocessing.scale(features, with_mean=True, with_std=True)
            else:
                raise ValueError("Unknown preprocessor: %s" % preprocessor_name)

            algorithm_name = algorithm["name"]
            if algorithm_name == "dbscan":
                eps = algorithm["params"]["eps"]
                min_samples = algorithm["params"]["min-samples"]
                metric = algorithm["params"]["metric"]
                labels = sklearn.cluster.DBSCAN(eps=eps, min_samples=min_samples, metric=metric).fit_predict(normalized)
                distances = [None] * len(labels)

            clusters = [{"oid": oid, "label": label, "distance": distance} for oid, label, distance in zip(oids, labels, distances)]

            return {
                "clusters": clusters,
                "content": content,
                "otype": otype,
            }


        def export_observations_impl(database_uri, database_name, search):
            database, fs = get_database(database_uri, database_name)
            observations = samlab.observation.search(database, search)

            roles = numpy.unique([role for observation in observations for role in observation["content"].keys() if observation["content"][role]["content-type"] in ["image/jpeg", "image/png"]])

            directory = tempfile.mkdtemp()
            log.info("Exporting observations to %s", directory)
            zpath = os.path.join(directory, "observations.zip")
            with zipfile.ZipFile(zpath, mode="w") as zfile:
                log.info("Creating zipfile %s", zpath)

                manifest = io.StringIO()
                manifest.write("_id")
                for role in roles:
                    manifest.write(",%s" % role)
                manifest.write("\n")
                for observation in observations:
                    manifest.write("%s" % observation["_id"])
                    for role in roles:
                        if role in observation["content"]:
                            rname = "%s-%s%s" % (observation["_id"], role, samlab.mime.lookup_extension(observation["content"][role]["content-type"]))
                            content = fs.get(observation["content"][role]["data"])
                            zfile.writestr(rname, content.read())
                            manifest.write(",%s" % rname)
                        else:
                            manifest.write(", ")
                    manifest.write("\n")
                zfile.writestr("manifest.csv", manifest.getvalue())

            return {
                "directory": directory,
                "count": len(observations),
            }


        self._queue = huey.RedisHuey("samlab-generic-queue")
        self.cluster_content = huey.api.TaskWrapper(self._queue, cluster_content_impl)
        self.export_observations = huey.api.TaskWrapper(self._queue, export_observations_impl)

    @property
    def queue(self):
        return self._queue

