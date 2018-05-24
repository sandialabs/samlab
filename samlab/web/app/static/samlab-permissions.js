// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout.mapping", "samlab-server"], function(mapping, server)
{
    var state = mapping.fromJS({
        permissions: {delete: false, developer: false, read: false, write: false},
    });

    server.load_json(state, "/permissions");

    return state.permissions;
});
