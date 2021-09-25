# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import flask

from samlab.dashboard import application, require_auth, require_permissions
from samlab.dashboard.service import require_backend


@application.route("/layouts", methods=["GET", "POST"])
@require_auth
def get_post_layouts():
    if flask.request.method == "GET":
        require_permissions(["read"])
        return flask.jsonify(layout=application.config["layout"])

    elif flask.request.method == "POST":
        require_permissions(["read"]) # We don't require write permissions to save a layout, by design.
        layouts = require_backend("layouts")
        lid = layouts.put(content=flask.request.json["layout"])
        return flask.jsonify(lid=lid)


@application.route("/layouts/<lid>")
@require_auth
def get_layouts_lid(lid):
    layouts = require_backend("layouts")
    layout = layouts.get(lid=lid)
    if layout is None:
        flask.abort(404)
    return flask.jsonify(layout=layout)


