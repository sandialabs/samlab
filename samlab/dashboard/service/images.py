# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import flask

from samlab.dashboard import application, require_auth, require_permissions, socketio
from samlab.dashboard.service import datasets, require_mapper


@application.route("/image-collection/<collection>")
@require_auth
def get_image_count(collection):
    require_permissions(["read"])
    image_collection = require_mapper(("image-collection", collection))
    return flask.jsonify(count=len(image_collection))


@application.route("/image-collection/<collection>/<int:index>")
@require_auth
def get_image(collection, index):
    require_permissions(["read"])
    image_collection = require_mapper(("image-collection", collection))
    image = image_collection.get(index)
    if isinstance(image, str):
        return flask.send_file(image)
    else:
        raise RuntimeError(f"Unknown image type: {type(image)}")


