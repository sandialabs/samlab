# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import flask

from samlab.dashboard import application, require_auth, require_permissions, socketio
from samlab.dashboard.service import datasets, require_backend


@application.route("/document-collection/<collection>")
@require_auth
def get_document_count(collection):
    require_permissions(["read"])
    document_collection = require_backend(("document-collection", collection))
    return flask.jsonify(count=len(document_collection))


@application.route("/document-collection/<collection>/<int:index>")
@require_auth
def get_document(collection, index):
    require_permissions(["read"])
    document_collection = require_backend(("document-collection", collection))
    document = document_collection.get(index)
    if isinstance(document, str):
        return flask.send_file(document)
    else:
        raise RuntimeError(f"Unknown document type: {type(document)}")


@application.route("/document-collection/<collection>/<int:index>/tags")
@require_auth
def get_document_tags(collection, index):
    require_permissions(["read"])
    document_collection = require_backend(("document-collection", collection))
    return flask.jsonify(tags=document_collection.tags(index))
