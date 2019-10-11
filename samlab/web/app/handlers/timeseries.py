# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import collections
import logging
import re

import flask
import numpy
import toyplot.bitmap
import toyplot.color
import toyplot.html

import samlab.timeseries

# Setup logging.
log = logging.getLogger(__name__)

# Get the web server.
from samlab.web.app import application, require_auth, require_permissions

# Get the database.
from samlab.web.app.database import database, fs


@application.route("/timeseries/keys")
@require_auth
def get_timeseries_keys():
    require_permissions(["read"])

    result = {}
    result["keys"] = sorted(database.timeseries.distinct("key"))

    return flask.jsonify(result)


@application.route("/timeseries/keys/series")
@require_auth
def get_timeseries_keys_series():
    require_permissions(["read"])

    keys = collections.defaultdict(list)
    for item in database.timeseries.aggregate([{"$group": {"_id": {"key": "$key", "series": "$series"}}}, {"$sort":{"_id": 1}}]):
        keys[item["_id"]["key"]].append(item["_id"]["series"])
    keys = [{"key":key, "series": series} for key, series in keys.items()]

    result = {}
    result["keys_series"] = keys

    return flask.jsonify(result)


@application.route("/timeseries/plots/auto")
@require_auth
def get_timeseries_plots_auto():
    require_permissions(["read"])

    height = int(float(flask.request.args.get("height", 500)))
    key = flask.request.args.get("key")
    smoothing = float(flask.request.args.get("smoothing", "0"))
    width = int(float(flask.request.args.get("width", 500)))
    yscale = flask.request.args.get("yscale", "linear")

    palette = toyplot.color.brewer.palette("Set2")
    canvas = toyplot.Canvas(width=width, height=height)
    axes = canvas.cartesian(xlabel="Step", yscale=yscale)

    steps = collections.defaultdict(list)
    values = collections.defaultdict(list)
    timestamps = collections.defaultdict(list)

    for sample in database.timeseries.find({"key": key}):
        series = sample.get("series", "default")
        step = sample["step"]
        value = sample["value"]
        timestamp = sample["timestamp"]
        steps[series].append(step)
        values[series].append(value)
        timestamps[series].append(timestamp)

    for series in steps:
        steps[series] = numpy.array(steps[series])
        values[series] = numpy.array(values[series])
        timestamps[series] = numpy.array(timestamps[series])

    for index, series in enumerate(steps):
        color = palette[hash(series) % len(palette)]

        # Display smoothed data.
        if smoothing:
            smoothed = []
            last = values[series][0]
            for value in values[series]:
                smoothed_val = last * smoothing + (1 - smoothing) * value
                smoothed.append(smoothed_val)
                last = smoothed_val
            axes.plot(steps[series], values[series], color=color, opacity=0.3, style={"stroke-width":1}, title=series)
            axes.plot(steps[series], smoothed, color=color, opacity=1, style={"stroke-width":2}, title="{} (smoothed)".format(series))
        # Just display the data
        else:
            axes.plot(steps[series], values[series], color=color, opacity=1, style={"stroke-width":2}, title=series)

    result = {}
    result["plot"] = toyplot.html.tostring(canvas)

    return flask.jsonify(result)


@application.route("/timeseries/samples", methods=["DELETE"])
@require_auth
def delete_timeseries_samples():
    require_permissions(["delete"])

    key = flask.request.args.get("key")
    series = flask.request.args.get("series", None)

    samlab.timeseries.delete(database, fs, key=key, series=series)
    return flask.jsonify()


