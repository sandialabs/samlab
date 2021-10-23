# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import hashlib

import flask
import scipy.signal
import toyplot.html
import xml.etree

from samlab.dashboard.server import application, require_auth, require_permissions
from samlab.dashboard.service import require_backend


@application.route("/timeseries-collection/<name>")
@require_auth
def get_timeseries(name):
    require_permissions(["read"])
    timeseries_collection = require_backend("timeseries-collection", name)
    count = len(timeseries_collection)
    keys = list(timeseries_collection.keys())
    return flask.jsonify(count=count, keys=keys)


@application.route("/timeseries-collection/<name>/plot", methods=["POST"])
@require_auth
def post_timeseries_plot(name):
    require_permissions(["read"])
    timeseries_collection = require_backend("timeseries-collection", name)

    height = int(float(flask.request.json.get("height", 500)))
    keys = flask.request.json.get("keys", [])
    legend_corner = flask.request.json.get("legend", "bottom-right")
    max_samples = int(float(flask.request.json.get("max_samples", 1000)))
    smoothing = float(flask.request.json.get("smoothing", "0"))
    width = int(float(flask.request.json.get("width", 500)))
    yscale = flask.request.json.get("yscale", "linear")

    timeseries = [timeseries_collection.get(key) for key in keys]

    canvas = toyplot.Canvas(width=width, height=height)
    axes = canvas.cartesian(xlabel="Step", yscale=yscale)

    palette = toyplot.color.brewer.palette("Set2")
    legend = []

    for key in keys:
        color_index = int(hashlib.sha256(key.encode("utf8")).hexdigest(), 16) % len(palette)
        color = palette[color_index]

        timeseries = timeseries_collection.get(key)
        if timeseries is None:
            continue
        if "values" not in timeseries:
            continue

        y = timeseries["values"]

        if "indices" in timeseries:
            indices = timeseries["indices"]
        else:
            indices = numpy.arange(len(y))
        x = indices

        if "markers" in timeseries:
            marker = timeseries["markers"]
        else:
            marker = [None] * len(y)

        if smoothing:
            alpha = 1 - smoothing
            b = [alpha]
            a = [1, alpha-1]
            zi = scipy.signal.lfiltic(b, a, y[0:1], [0])
            ys = scipy.signal.lfilter(b, a, y, zi=zi)[0]
            axes.plot(x, y, color=color, opacity=0.25)
            legend.append((key, axes.plot(x, ys, color=color, marker=marker)))
        else:
            legend.append((key, axes.plot(x, y, color=color, marker=marker)))

    if legend:
        height = len(legend) * 16
        inset = 50
        canvas.legend(legend, corner=(legend_corner, inset, 100, height))

    return flask.jsonify({"plot": toyplot.html.tostring(canvas)})

