// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-server",
    "samlab-socket",
    "URI",
    ], function(debug, ko, mapping, server, socket, URI)
{
    var log = debug("samlab-timeseries");

    var module = mapping.fromJS({
        experiments: [],
        keys: [],
        timeseries: [],
        on_show: null,
        on_hide: null,
        sample: {
            created: null,
            updated: null,
            deleted: null,
        },
    });

    module.sample.created.extend({notify: "always"});
    module.sample.updated.extend({notify: "always"});
    module.sample.deleted.extend({notify: "always", rateLimit: {timeout: 500, method: "notifyWhenChangesStop"}});

    module.on_show.extend({notify: "always"});
    module.on_hide.extend({notify: "always"});

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

    // Load timeseries metadata at startup and anytime there are changes, but limit the rate.
    var load_metadata = ko.computed(function()
    {
        server.load_json(module, "/timeseries/metadata");

        // Register the observables we want to track
        module.sample.created();
        module.sample.updated();
        module.sample.deleted();
    }).extend({notify: "always", rateLimit: {timeout: 500, method: "notifyWhenChangesStop"}});

    module.delete_samples = function(params)
    {
        var uri = URI("/timeseries/samples");

        if(params.experiment)
            uri.addQuery("experiment", params.experiment);
        if(params.trial)
            uri.addQuery("trial", params.trial);
        if(params.key)
            uri.addQuery("key", params.key);

        server.delete(uri);
    };

    module.show = function(params)
    {
        module.on_show(params);
    }

    module.hide = function(params)
    {
        module.on_hide(params);
    }

    return module;
});

