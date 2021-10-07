# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import flask

from samlab.dashboard import application, require_auth, require_permissions
from samlab.dashboard.service import require_backend


@application.route("/timeseries-collection/<name>")
@require_auth
def get_timeseries_count(name):
    require_permissions(["read"])
    timeseries_collection = require_backend("timeseries-collection", name)
    return flask.jsonify(count=len(timeseries_collection))


@application.route("/timeseries-collection/<name>/<int:index>")
@require_auth
def get_timeseries(name, index):
    require_permissions(["read"])
    timeseries_collection = require_backend("timeseries-collection", name)
    timeseries = timeseries_collection.get(index)
    if isinstance(timeseries, str):
        return flask.send_file(timeseries)
    else:
        raise RuntimeError(f"Unknown timeseries type: {type(timeseries)}")


