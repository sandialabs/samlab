// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-server",
    ], function(ko, mapping, server)
{
    var module = mapping.fromJS({
    });

    module.delete = function(id)
    {
        server.load_json(module, "/observations/" + id, "DELETE");
    };

    return module;
});
