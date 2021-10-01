// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-server",
    "samlab-socket",
    "URI",
    ], function(debug, ko, mapping, server, socket, URI)
{
    var log = debug("samlab-object-manager");

    var module = mapping.fromJS({
        changed: null,
        created: null,
        deleted: null,
    });

    module.changed.extend({notify: "always"});
    module.created.extend({notify: "always"});
    module.deleted.extend({notify: "always"});

    socket.on("object-changed", function(object)
    {
        log("object changed", object);
        module.changed(object);
    });

    socket.on("object-created", function(object)
    {
        log("object created", object);
        module.created(object);
    });

    socket.on("object-deleted", function(object)
    {
        log("object deleted", object);
        module.deleted(object);
    });

    module.label = function(otype, params)
    {
        var params = params || {};
        var result = ko.unwrap(otype);
        if(params.singular)
            result = result.substr(0, result.length-1);
        if(params.capitalize)
            result = result.substr(0, 1).toUpperCase() + result.substr(1);
        return result;
    }

    return module;
});

