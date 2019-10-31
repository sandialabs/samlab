// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout", "knockout.mapping", "samlab-server", "samlab-socket"], function(ko, mapping, server, socket)
{
    var module = mapping.fromJS({
        deliveries: [],
    });

    module.delete_delivery = function(did)
    {
        server.load_json(module, "/deliveries/" + did, "DELETE");
    };

    socket.on("object-created", function(object)
    {
        if(object.otype == "deliveries")
            server.load_json(module, "/deliveries");
    });

    socket.on("object-changed", function(object)
    {
        if(object.otype == "deliveries")
            server.load_json(module, "/deliveries");
    });

    socket.on("object-deleted", function(object)
    {
        if(object.otype == "deliveries")
            server.load_json(module, "/deliveries");
    });

    server.load_json(module, "/deliveries");

    return module;
});
