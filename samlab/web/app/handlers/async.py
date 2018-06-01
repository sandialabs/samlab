# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging

import arrow
import flask

import samlab.tasks.generic
import samlab.tasks.gpu

# Setup logging.
log = logging.getLogger(__name__)

# Get the web server.
from samlab.web.app import application, socketio, require_auth, require_permissions

# Get the database.
from samlab.web.app.database import database, fs

# Setup task queues
generic_queue = samlab.tasks.generic.Queue()
gpu_queue = samlab.tasks.gpu.Queue("samlab-gpu-0")


def log_request():
    log.info("socket.io client %s: %s", flask.request.sid, flask.request.event["message"])


def receive_delivery(directory, label):
    document = {
        "created": arrow.utcnow().datetime,
        "directory": directory,
        "label": label,
    }
    did = database.deliveries.insert_one(document).inserted_id
    log.info("Delivery received: %s %s", directory, label)
    socketio.emit("notify", {"icon": "fa fa-truck", "message": "Delivery received: %s" % label, "type": "success", "delay": 0})


##################################################################################
# Asynchronous endpoints

@socketio.on("connect")
@require_auth
def connect():
    require_permissions(["read"])
    log_request()


@socketio.on("cluster-content")
@require_auth
def cluster_content(params):
    require_permissions(["read"])
    log_request()

    sid = flask.request.sid
    database_uri = application.config["database-uri"]
    database_name = application.config["database-name"]
    otype = params["otype"]
    content = params["content"]
    preprocessor = params["preprocessor"]
    algorithm = params["algorithm"]

    assert(otype in ["observations"])


    def implementation(*args, **kwargs):
        task = generic_queue.cluster_content(*args, **kwargs)
        while True:
            result = task()
            if result is not None:
                socketio.emit("cluster-content", result, room=sid)
                return
            socketio.sleep(1.0)
    socketio.start_background_task(implementation, database_uri, database_name, otype, content, preprocessor, algorithm)


@socketio.on("disconnect")
@require_auth
def disconnect():
    log_request()


@socketio.on("export-observations")
@require_auth
def export_observations(params):
    require_permissions(["read"])
    log_request()

    sid = flask.request.sid
    database_uri = application.config["database-uri"]
    database_name = application.config["database-name"]
    search = params["search"]

    def implementation(*args, **kwargs):
        task = generic_queue.export_observations(*args, **kwargs)
        while True:
            result = task()
            if result is not None:
                receive_delivery(result["directory"], "Exported %s observations" % result["count"])
                return
            socketio.sleep(1.0)
    socketio.start_background_task(implementation, database_uri, database_name, search)


@socketio.on("keras-model-evaluate-images")
@require_auth
def keras_model_evaluate_images(params):
    require_permissions(["read"])
    log_request()

    sid = flask.request.sid
    database_uri = application.config["database-uri"]
    database_name = application.config["database-name"]
    mid = params["mid"]

    def implementation(mid):
        task = gpu_queue.get_model_evaluate_images(application.config["database-uri"], application.config["database-name"], mid)
        while True:
            evaluation = task()
            if evaluation is not None:
                observations = [str(observation["_id"]) for observation in evaluation["observations"]]
                outputs = evaluation["outputs"].tolist()
                predictions = evaluation["predictions"].tolist()
                matches = evaluation["matches"].tolist()

                images = [{"observation": observation, "output": output, "prediction": prediction, "match": match} for observation, output, prediction, match in zip(observations, outputs, predictions, matches)]
                images = sorted(images, key=lambda x: x["prediction"])
                socketio.emit("keras-model-evaluate-images", {"mid": mid, "images": images}, room=sid)
                return
            socketio.sleep(0.5)
    socketio.start_background_task(implementation, mid)


@socketio.on("keras-model-layer-filter-gradient-ascent")
@require_auth
def keras_model_layer_filter_gradient_ascent(params):
    require_permissions(["read"])
    log_request()

    sid = flask.request.sid
    database_uri = application.config["database-uri"]
    database_name = application.config["database-name"]
    otype = params["otype"]
    oid = params["oid"]
    key = params["key"]
    layer = params["layer"]
    filter = params["filter"]

    cache_key = (otype, oid, key, layer, filter)
    if cache_key in keras_model_layer_filter_gradient_ascent.cache:
        image = keras_model_layer_filter_gradient_ascent.cache[cache_key]
        image = toyplot.bitmap.to_png_data_uri(image)
        socketio.emit("keras-model-layer-filter-gradient-ascent", {"otype": otype, "oid": oid, "key": key, "layer": layer, "filter": filter, "image": image}, room=sid)
        return

    def implementation(otype, oid, key, layer, filter):
        task = gpu_queue.get_model_layer_filter_gradient_ascent(database_uri, database_name, otype, oid, key, layer, filter)
        while True:
            result = task()
            if result is not None:
                keras_model_layer_filter_gradient_ascent.cache[cache_key] = result
                image = keras_model_layer_filter_gradient_ascent.cache[cache_key]
                image = toyplot.bitmap.to_png_data_uri(image)
                socketio.emit("keras-model-layer-filter-gradient-ascent", {"otype": otype, "oid": oid, "key": key, "layer": layer, "filter": filter, "image": image}, room=sid)
                return
            socketio.sleep(0.5)
    socketio.start_background_task(implementation, otype, oid, key, layer, filter)
keras_model_layer_filter_gradient_ascent.cache = {}


@socketio.on("keras-model-summary")
@require_auth
def keras_model_summary(params):
    require_permissions(["read"])
    log_request()

    sid = flask.request.sid
    database_uri = application.config["database-uri"]
    database_name = application.config["database-name"]
    otype = params["otype"]
    oid = params["oid"]
    key = params["key"]

    cache_key = (otype, oid, key)
    if cache_key in keras_model_summary.cache:
        socketio.emit("keras-model-summary", {"otype": otype, "oid": oid, "key": key, "summary": keras_model_summary.cache[cache_key]}, room=sid)
        return

    def implementation(otype, oid, key):
        task = gpu_queue.get_model_summary(database_uri, database_name, otype, oid, key)
        while True:
            result = task()
            if result is not None:
                keras_model_summary.cache[cache_key] = result
                socketio.emit("keras-model-summary", {"otype": otype, "oid": oid, "key": key, "summary": keras_model_summary.cache[cache_key]}, room=sid)
                return
            socketio.sleep(0.5)
    socketio.start_background_task(implementation, otype, oid, key)
keras_model_summary.cache = {}


@socketio.on("test")
@require_auth
def test():
    require_permissions(["read"])
    log_request()
    socketio.emit("test")


