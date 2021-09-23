// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["samlab-server", "samlab-socket"/*, "bootstrap-notify"*/], function(server, socket)
{
    var module = {};

    module.local = function(params)
    {
        $.notify(
        {
            icon: params.icon || "",
            message: params.message || "",
            title: params.title || "",
        },
        {
            allow_dismiss: true,
            delay: params.delay || 8000,
            newest_on_top: true,
            type: params.type || "primary",
        });
    }

    module.broadcast = function(params)
    {
        server.post_json("/notify", params);
    }

    socket.on("notify", function(params)
    {
        module.local(params);
    });

    return module;
});
