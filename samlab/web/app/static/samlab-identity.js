// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout.mapping", "samlab-server"], function(mapping, server)
{
    var module = mapping.fromJS({
        username: null,
    });

    server.load_json(module, "/identity");

    return module;
});
