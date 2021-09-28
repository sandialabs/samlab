// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout", "knockout.mapping", "samlab-server"], function(ko, mapping, server)
{
    var module = mapping.fromJS({
        backends: [],
    });

    function load_backends()
    {
        server.load_json(module, "/backends");
    }

/*
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
*/

    load_backends();

    return module;
});
