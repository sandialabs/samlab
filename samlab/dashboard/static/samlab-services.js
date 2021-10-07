// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-server",
    ], function(debug, ko, mapping, server)
{
    var log = debug("samlab-services");

    var module = mapping.fromJS({
        backends: [],
    });

    module.label = function(service)
    {
        if(service == "layouts")
            return "Layouts";
        else if(service == "favorites")
            return "Favorites";
        return service;
    }
    function load_backends()
    {
        server.load_json(module, "/backends");
    }

    load_backends();

    return module;
});
