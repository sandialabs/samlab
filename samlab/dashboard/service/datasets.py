# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import flask

from samlab.dashboard import application, require_auth, require_permissions
import samlab.dashboard.service


@application.route("/datasets")
@require_auth
def get_datasets():
    require_permissions(["read"])
    return flask.jsonify(datasets=sorted(samlab.dashboard.service.get_datasets()))


