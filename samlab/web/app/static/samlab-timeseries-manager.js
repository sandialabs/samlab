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
        exclude: [],
        sample: {
            created: null,
            updated: null,
            deleted: null,
        },
    });

    module.sample.created.extend({notify: "always"});
    module.sample.updated.extend({notify: "always"});
    module.sample.deleted.extend({notify: "always"});

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
        // Register the observables we want to track.
        module.sample.created();
        module.sample.updated();
        module.sample.deleted();

        // Load the new metadata.
        server.load_json(module, "/timeseries/metadata");

    }).extend({notify: "always", rateLimit: {timeout: 500}});

    module.delete_samples = function(params)
    {
        var uri = URI("/timeseries/samples");

        if(params.experiment)
            uri.addQuery("experiment", ko.unwrap(params.experiment));
        if(params.trial)
            uri.addQuery("trial", ko.unwrap(params.trial));
        if(params.key)
            uri.addQuery("key", ko.unwrap(params.key));

        server.delete(uri);
    };

    module.exclude.subscribe(function()
    {
        log("global timeseries exclude changed:", mapping.toJS(module.exclude()));
    });

    return module;
});

