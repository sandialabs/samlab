# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import flask

from samlab.web.app import application, require_auth, require_permissions, socketio
from samlab.dashboard.service import datasets, require_mapper


@application.route("/images")
@require_auth
def get_images():
    require_permissions(["read"])
    return flask.jsonify(datasets=list(datasets(service="images")))


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

