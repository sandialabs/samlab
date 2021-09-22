# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import flask

from samlab.web.app import application, require_auth, require_permissions, socketio
from samlab.dashboard.service import datasets, require_mapper


@application.route("/images/<dataset>")
@require_auth
def get_image_count(dataset):
    require_permissions(["read"])
    image_collection = require_mapper(("images", dataset))
    return flask.jsonify(images=len(image_collection))


@application.route("/images/<dataset>/<int:index>")
@require_auth
def get_image(dataset, index):
    require_permissions(["read"])
    image_collection = require_mapper(("images", dataset))
    image = image_collection.get(index)
    if isinstance(image, str):
        return flask.send_file(image)
    else:
        raise RuntimeError(f"Unknown image type: {type(image)}")

#@application.route("/favorites/<allow(layouts):otype>/<oid>", methods=["PUT", "DELETE"])
#@require_auth
#def put_delete_favorites_otype_oid(otype, oid):
#    if flask.request.method == "PUT":
#        require_permissions(["write"])
#        name = flask.request.json["name"]
#        favorites = require_mapper("favorites")
#        if favorites.contains(otype, oid):
#            favorites.create(otype, oid, name)
#            socketio.emit("object-changed", {"otype": "favorites", "oid": oid})
#        else:
#            favorites.create(otype, oid, name)
#            socketio.emit("object-created", {"otype": "favorites", "oid": oid})
#        return flask.jsonify()
#
#    elif flask.request.method == "DELETE":
#        require_permissions(["delete"])
#        require_mapper("favorites").delete(otype, oid)
#        socketio.emit("object-deleted", {"otype": "favorites", "oid": oid})
#        return flask.jsonify()

