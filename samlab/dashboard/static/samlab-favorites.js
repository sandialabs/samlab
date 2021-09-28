// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-object-manager",
    "samlab-server",
    ], function(ko, mapping, object, server)
{
    var module = mapping.fromJS({
        favorites: [],
    });

    module.get = function(otype, oid)
    {
        var otype = ko.unwrap(otype);
        var oid = ko.unwrap(oid);
        for(let favorite of module.favorites())
        {
            if(otype == favorite.otype() && oid == favorite.oid())
                return true;
        }
        return false;
    };

    module.create = function(otype, oid, name)
    {
        var otype = ko.unwrap(otype);
        var oid = ko.unwrap(oid);
        var name = ko.unwrap(name);
        server.put_json("/favorites/" + otype + "/" + oid, {name: name});
    };

    module.delete = function(otype, oid)
    {
        var otype = ko.unwrap(otype);
        var oid = ko.unwrap(oid);
        server.delete("/favorites/" + otype + "/" + oid);
    };

    function load_favorites()
    {
        server.load_json(module, "/favorites");
    }

    object.changed.subscribe(function(object)
    {
        if(object.otype == "favorites")
        {
            load_favorites();
        }
    });

    object.created.subscribe(function(object)
    {
        if(object.otype == "favorites")
        {
            load_favorites();
        }
    });

    object.deleted.subscribe(function(object)
    {
        if(object.otype == "favorites")
        {
            load_favorites();
        }
    });

    load_favorites();

    return module;
});
