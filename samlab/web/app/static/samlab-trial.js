// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-object",
    "samlab-server",
    ], function(ko, mapping, object, server)
{
    var module = mapping.fromJS({
        trials: [],
    });

    function load_trials()
    {
        server.load_json(module, "/trials?sort=created");
    }

    module.delete = function(id)
    {
        server.load_json(module, "/trials/" + id, "DELETE");
    };

    object.changed.subscribe(function(object)
    {
        if(object.otype == "trials")
        {
            load_trials();
        }
    });

    object.created.subscribe(function(object)
    {
        if(object.otype == "trials")
        {
            load_trials();
        }
    });

    object.deleted.subscribe(function(object)
    {
        if(object.otype == "trials")
        {
            load_trials();
        }
    });

    load_trials();

    return module;
});
