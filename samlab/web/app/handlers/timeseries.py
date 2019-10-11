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


@application.route("/timeseries/metadata")
@require_auth
def get_timeseries_metadata():
    require_permissions(["read"])

    experiment_trials = collections.defaultdict(set)
    experiment_keys = collections.defaultdict(set)
    trial_experiments = collections.defaultdict(set)
    trial_keys = collections.defaultdict(set)
    key_experiments = collections.defaultdict(set)
    key_trials = collections.defaultdict(set)

    for item in database.timeseries.aggregate([{"$group": {"_id": {"experiment": "$experiment", "trial": "$trial", "key": "$key"}}}, {"$sort":{"_id": 1}}]):
        experiment_trials[item["_id"]["experiment"]].add(item["_id"]["trial"])
        experiment_keys[item["_id"]["experiment"]].add(item["_id"]["key"])
        trial_experiments[item["_id"]["trial"]].add(item["_id"]["experiment"])
        trial_keys[item["_id"]["trial"]].add(item["_id"]["key"])
        key_experiments[item["_id"]["key"]].add(item["_id"]["experiment"])
        key_trials[item["_id"]["key"]].add(item["_id"]["trial"])


    palette = toyplot.color.brewer.palette("Set2")

    result = {}
    result["experiments"] = [{"experiment": experiment, "keys": sorted(experiment_keys[experiment]), "trials": sorted(experiment_trials[experiment])} for experiment in sorted(experiment_trials.keys())]
    result["trials"] = [{"trial": trial, "color": toyplot.color.to_css(palette[hash(trial) % len(palette)]), "experiments": sorted(trial_experiments[trial]), "keys": sorted(trial_keys[trial])} for trial in sorted(trial_experiments.keys())]
    result["keys"] = [{"key":key, "experiments": sorted(key_experiments[key]), "trials": sorted(key_trials[key])} for key in sorted(key_experiments.keys())]

    return flask.jsonify(result)


@application.route("/timeseries/plots/auto")
@require_auth
def get_timeseries_plots_auto():
    require_permissions(["read"])

    experiment = flask.request.args.get("experiment")
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

    for sample in database.timeseries.find({"experiment": experiment, "key": key}):
        series = sample.get("trial")
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

    experiment = flask.request.args.get("experiment", None)
    trial = flask.request.args.get("trial", None)
    key = flask.request.args.get("key", None)

    samlab.timeseries.delete(database, fs, experiment=experiment, trial=trial, key=key)

    return flask.jsonify()


