// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-server",
    "samlab-socket",
    ], function(debug, ko, mapping, server, socket)
{
    var log = debug("samlab-favorites");

    var module = mapping.fromJS({
        favorites: [],
    });

    module.get = function(service, name)
    {
        var service = ko.unwrap(service);
        var name = ko.unwrap(name);
        for(let favorite of module.favorites())
        {
            if(service == favorite.service() && name == favorite.name())
                return true;
        }
        return false;
    };

    module.create = function(service, name, label)
    {
        var service = ko.unwrap(service);
        var name = ko.unwrap(name);
        var label = ko.unwrap(label);
        server.put_json("/favorites/" + service + "/" + name, {label: label});
    };

    module.delete = function(service, name)
    {
        var service = ko.unwrap(service);
        var name = ko.unwrap(name);
        server.delete("/favorites/" + service + "/" + name);
    };

    function load_favorites()
    {
        server.load_json(module, "/favorites");
    }

    socket.on("favorite-changed", function(object)
    {
        log("favorite-changed", object);
        load_favorites();
    });

    socket.on("favorite-created", function(object)
    {
        log("favorite-created", object);
        load_favorites();
    });

    socket.on("favorite-deleted", function(object)
    {
        log("favorite-deleted", object);
        load_favorites();
    });

    load_favorites();

    return module;
});
