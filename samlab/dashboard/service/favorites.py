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
    return flask.jsonify(favorites=favorites.get())


@application.route("/favorites/<allow(layouts):service>/<name>", methods=["PUT", "DELETE"])
@require_auth
def put_delete_favorites_service_name(service, name):
    if flask.request.method == "PUT":
        require_permissions(["write"])
        label = flask.request.json["label"]
        require_backend("favorites").create(service, name, label)
        return flask.jsonify()

    elif flask.request.method == "DELETE":
        require_permissions(["delete"])
        require_backend("favorites").delete(service, name)
        return flask.jsonify()

