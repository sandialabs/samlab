# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import flask

from samlab.dashboard import application, require_auth, require_permissions, socketio
from samlab.dashboard.service import require_backend


@application.route("/favorites")
@require_auth
def get_favorites():
    require_permissions(["read"])
    favorites = require_backend("favorites")
    return flask.jsonify(favorites=list(favorites.get()))


@application.route("/favorites/<allow(layouts):otype>/<oid>", methods=["PUT", "DELETE"])
@require_auth
def put_delete_favorites_otype_oid(otype, oid):
    if flask.request.method == "PUT":
        require_permissions(["write"])
        name = flask.request.json["name"]
        favorites = require_backend("favorites")
        if favorites.contains(otype, oid):
            favorites.create(otype, oid, name)
            socketio.emit("object-changed", {"otype": "favorites", "oid": oid})
        else:
            favorites.create(otype, oid, name)
            socketio.emit("object-created", {"otype": "favorites", "oid": oid})
        return flask.jsonify()

    elif flask.request.method == "DELETE":
        require_permissions(["delete"])
        require_backend("favorites").delete(otype, oid)
        socketio.emit("object-deleted", {"otype": "favorites", "oid": oid})
        return flask.jsonify()

