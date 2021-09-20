# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import flask

# Get the web server.
from samlab.web.app import application, require_auth, require_permissions
from samlab.dashboard.service import require_mapper


@application.route("/favorites")
@require_auth
def get_favorites():
    require_permissions(["read"])
    favorites = require_mapper("favorites").get()
    return flask.jsonify(favorites=list(favorites))


@application.route("/favorites/<allow(layouts):otype>/<oid>", methods=["PUT", "DELETE"])
@require_auth
def put_delete_favorites_otype_oid(otype, oid):
    if flask.request.method == "PUT":
        require_permissions(["write"])
        name = flask.request.json["name"]
        require_mapper("favorites").create(otype, oid, name)
        return flask.jsonify()

    elif flask.request.method == "DELETE":
        require_permissions(["delete"])
        require_mapper("favorites").delete(otype, oid)
        return flask.jsonify()

