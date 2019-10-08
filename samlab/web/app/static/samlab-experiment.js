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
        experiments: [],
    });

    function load_experiments()
    {
        server.load_json(module, "/experiments?sort=created");
    }

    module.delete = function(id)
    {
        server.load_json(module, "/experiments/" + id, "DELETE");
    };

    object.changed.subscribe(function(object)
    {
        if(object.otype == "experiments")
        {
            load_experiments();
        }
    });

    object.created.subscribe(function(object)
    {
        if(object.otype == "experiments")
        {
            load_experiments();
        }
    });

    object.deleted.subscribe(function(object)
    {
        if(object.otype == "experiments")
        {
            load_experiments();
        }
    });

    load_experiments();

    return module;
});
