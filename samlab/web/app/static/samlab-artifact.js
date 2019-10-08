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
    });

    module.delete = function(id)
    {
        server.load_json(module, "/artifacts/" + id, "DELETE");
    };

    return module;
});
