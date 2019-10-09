# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import hashlib
import json
import logging

import flask

# Setup logging.
log = logging.getLogger(__name__)

# Get the web server.
from samlab.web.app import application, require_auth, require_permissions

# Get the database.
from samlab.web.app.database import database, fs


@application.route("/layouts", methods=["GET", "POST"])
@require_auth
def get_post_layouts():
    if flask.request.method == "GET":
        require_permissions(["read"])
        return flask.jsonify(layout=application.config["layout"])

    elif flask.request.method == "POST":
        require_permissions(["read"]) # We don't require write permissions to save a layout, by design.

        #log.info(flask.request.json["layout"])

        content = json.dumps(flask.request.json["layout"], separators=(",",":"), indent=None, sort_keys=True)
        lid = hashlib.md5(content.encode("utf8")).hexdigest()

        layout = database.layouts.find_one({"lid": lid})
        if layout is None:
            database.layouts.insert_one({"lid": lid, "content": content})

        return flask.jsonify(lid=str(lid))

@application.route("/layouts/<lid>")
@require_auth
def get_layouts_lid(lid):
    layout = database.layouts.find_one({"lid": lid})
    if layout is None:
        flask.abort(404)
    return flask.jsonify(layout=json.loads(layout["content"]))


