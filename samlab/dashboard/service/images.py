# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import flask

from samlab.dashboard import application, require_auth, require_permissions, socketio
from samlab.dashboard.service import require_backend


@application.route("/image-collection/<name>")
@require_auth
def get_image_collection(name):
    require_permissions(["read"])
    image_collection = require_backend("image-collection", name)
    return flask.jsonify(count=len(image_collection))


@application.route("/image-collection/<name>/categories")
@require_auth
def get_image_collection_categories(name):
    require_permissions(["read"])
    image_collection = require_backend("image-collection", name)
    return flask.jsonify({"categories": image_collection.categories})


@application.route("/image-collection/<name>/<int:index>")
@require_auth
def get_image(name, index):
    require_permissions(["read"])
    image_collection = require_backend("image-collection", name)
    image = image_collection.get(index)
    if isinstance(image, str):
        return flask.send_file(image)
    else:
        raise RuntimeError(f"Unknown image type: {type(image)}")


@application.route("/image-collection/<name>/<int:index>/bboxes", methods=["GET", "PUT"])
@require_auth
def get_put_image_bboxes(name, index):
    if flask.request.method == "GET":
        require_permissions(["read"])
        image_collection = require_backend("image-collection", name)
        return flask.jsonify(bboxes=image_collection.bboxes(index))

    if flask.request.method == "PUT":
        require_permissions(["write"])

        bboxes = flask.request.json["bboxes"]
        for bbox in bboxes:
            for key in ["left", "top", "width", "height", "category"]:
                if key not in bbox:
                    flask.abort(flask.make_response(flask.jsonify(message="Bounding box missing required key: {key}"), 400))

            if not bbox["category"]:
                flask.abort(flask.make_response(flask.jsonify(message="Bounding box category cannot be empty."), 400))

        image_collection = require_backend("image-collection", name)
        saved = image_collection.put_bboxes(index, bboxes)
        if not saved:
            flask.abort(flask.make_response(flask.jsonify(message="This dataset is read-only."), 400))

        return flask.jsonify()


@application.route("/image-collection/<name>/<int:index>/metadata")
@require_auth
def get_image_metadata(name, index):
    require_permissions(["read"])
    image_collection = require_backend("image-collection", name)
    return flask.jsonify(metadata=image_collection.metadata(index))


@application.route("/image-collection/<name>/<int:index>/tags", methods=["GET", "PUT"])
@require_auth
def get_put_image_tags(name, index):
    if flask.request.method == "GET":
        require_permissions(["read"])
        image_collection = require_backend("image-collection", name)
        return flask.jsonify(tags=image_collection.tags(index))

    if flask.request.method == "PUT":
        require_permissions(["write"])

        tags = flask.request.json["tags"]
        for tag in tags:
            if not tag:
                flask.abort(flask.make_response(flask.jsonify(message="Tag category cannot be empty."), 400))

        image_collection = require_backend("image-collection", name)
        saved = image_collection.put_tags(index, tags)
        if not saved:
            flask.abort(flask.make_response(flask.jsonify(message="This dataset is read-only."), 400))

        return flask.jsonify()

