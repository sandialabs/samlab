// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-server",
    "samlab-socket",
    ], function(debug, ko, mapping, server, socket)
{
    var log = debug("samlab-timeseries");

    var module = mapping.fromJS({
        keys: [],
        sample: {
            created: null,
            updated: null,
            deleted: null,
        },
    });

    module.sample.created.extend({notify: "always"});
    module.sample.updated.extend({notify: "always"});
    module.sample.deleted.extend({notify: "always", rateLimit: {timeout: 500, method: "notifyWhenChangesStop"}});

    socket.on("timeseries-sample-created", function(object)
    {
        module.sample.created(object);
    });

    socket.on("timeseries-sample-updated", function(object)
    {
        module.sample.updated(object);
    });

    socket.on("timeseries-sample-deleted", function(object)
    {
        module.sample.deleted(object);
    });

    // Load timeseries keys at startup and anytime there are changes, but limit the rate.
    var load_keys = ko.computed(function()
    {
        log("Loading timeseries keys.");
        server.load_json(module, "/timeseries/keys");

        // Register the observables we want to track
        module.sample.created();
        module.sample.updated();
        module.sample.deleted();
    }).extend({notify: "always", rateLimit: {timeout: 500, method: "notifyWhenChangesStop"}});

    module.delete_samples = function(key)
    {
        server.delete("/timeseries/samples?key=" + key);
    };

    return module;
});

