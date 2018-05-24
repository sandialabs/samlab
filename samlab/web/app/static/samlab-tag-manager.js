// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout", "knockout.mapping", "samlab-server", "samlab-socket"], function(ko, mapping, server, socket)
{
    var module = mapping.fromJS({
        otype: null,
        oid: null,
        tags: [],
    });

    module.otype.subscribe(function(otype)
    {
        if(otype)
        {
            server.load_json(module, "/" + otype + "/tags");
        }
        else
        {
            module.tags([]);
        }
    });

    module.manage = function(otype, oid)
    {
        module.otype(ko.utils.unwrapObservable(otype));
        module.oid(ko.utils.unwrapObservable(oid));
    }

    module.release = function(otype, oid)
    {
        if(module.otype() != ko.utils.unwrapObservable(otype))
            return;
        if(module.oid() != ko.utils.unwrapObservable(oid))
            return;

        module.otype(null);
        module.oid(null);
    }

    module.add_tag = function(tag)
    {
        server.put_json("/" + module.otype() + "/" + module.oid() + "/tags", {add: [tag], remove: [], toggle: []});
    }

    module.remove_tag = function(tag)
    {
        server.put_json("/" + module.otype() + "/" + module.oid() + "/tags", {add: [], remove: [tag], toggle: []});
    }

    module.toggle_tag = function(tag)
    {
        server.put_json("/" + module.otype() + "/" + module.oid() + "/tags", {add: [], remove: [], toggle: [tag]});
    }

    socket.on("tags-changed", function(otype)
    {
        if(otype == module.otype())
        {
            server.load_json(module, "/" + otype + "/tags");
        }
    });

    return module;
});
