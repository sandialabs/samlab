# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import flask

from samlab.dashboard import application, require_auth, require_permissions, socketio
from samlab.dashboard.service import require_backend


@application.route("/image-collection/<collection>")
@require_auth
def get_image_collection(collection):
    require_permissions(["read"])
    image_collection = require_backend("image-collection", collection)
    return flask.jsonify(count=len(image_collection))


@application.route("/image-collection/<collection>/<int:index>")
@require_auth
def get_image(collection, index):
    require_permissions(["read"])
    image_collection = require_backend("image-collection", collection)
    image = image_collection.get(index)
    if isinstance(image, str):
        return flask.send_file(image)
    else:
        raise RuntimeError(f"Unknown image type: {type(image)}")


@application.route("/image-collection/<collection>/<int:index>/bboxes", methods=["GET", "PUT"])
@require_auth
def get_put_image_bboxes(collection, index):
    if flask.request.method == "GET":
        require_permissions(["read"])
        image_collection = require_backend("image-collection", collection)
        return flask.jsonify(bboxes=image_collection.bboxes(index))

    elif flask.request.method == "PUT":
        require_permissions(["write"])
        bboxes = flask.request.json["bboxes"]
        image_collection = require_backend("image-collection", collection)
        image_collection.put_bboxes(index, bboxes)
        return flask.jsonify()


@application.route("/image-collection/<collection>/<int:index>/metadata")
@require_auth
def get_image_metadata(collection, index):
    require_permissions(["read"])
    image_collection = require_backend("image-collection", collection)
    return flask.jsonify(metadata=image_collection.metadata(index))


@application.route("/image-collection/<collection>/<int:index>/tags")
@require_auth
def get_image_tags(collection, index):
    require_permissions(["read"])
    image_collection = require_backend("image-collection", collection)
    return flask.jsonify(tags=image_collection.tags(index))
