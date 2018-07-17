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
    var log = debug("samlab-object");

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

    module.notify_changed = function(otype, oid, callback)
    {
        var otype = ko.unwrap(otype);
        var oid = ko.unwrap(oid);
        return module.changed.subscribe(function(object)
        {
            if(otype == object.otype && oid == object.oid)
            {
                callback();
            }
        });
    }

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

    module.delete_content = function(otype, oid, key)
    {
        var otype = ko.unwrap(otype);
        var oid = ko.unwrap(oid);
        var key = ko.unwrap(key);

        log("delete content", otype, oid, key);

        server.delete("/" + otype + "/" + oid + "/content/" + key, "DELETE");
    }

    module.lookup_count = function(otype, params)
    {
        var params = params || {};

        var uri = URI("/" + otype + "/count").setQuery(
        {
            session: params.session || "",
            search: params.search || "",
        });

        server.get_json(uri,
        {
            success: params.success,
            error: params.error,
            finished: params.finished,
        });
    }

    module.lookup_index = function(otype, oid, params)
    {
        var params = params || {};

        var uri = URI("/" + otype + "/id/" + oid).setQuery(
        {
            session: params.session || "",
            search: params.search || "",
            sort: params.sort || "",
            direction: params.direction || "",
        });

        server.get_json(uri,
        {
            success: params.success,
            error: params.error,
            finished: params.finished,
        });
    }

    module.lookup_id = function(otype, oindex, params)
    {
        var params = params || {};

        var uri = URI("/" + otype + "/index/" + oindex).setQuery(
        {
            session: params.session || "",
            search: params.search || "",
            sort: params.sort || "",
            direction: params.direction || "",
        });

        server.get_json(uri,
        {
            success: params.success,
            error: params.error,
            finished: params.finished,
        });
    }

    return module;
});

