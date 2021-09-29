// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-server",
    ], function(debug, ko, mapping, dashboard, server)
{
    var log = debug("samlab-backends");

    var module = mapping.fromJS({
        backends: [],
    });

    module.view = function(service, name)
    {
        log("view", service, name);
        if(service == "favorites")
        {
            dashboard.add_widget("samlab-favorites-widget");
        }
        else if(service == "document-collection")
        {
            dashboard.add_widget("samlab-documents-widget", {collection: name, index: 0});
        }
        else if(service == "image-collection")
        {
            dashboard.add_widget("samlab-images-widget", {collection: name, index: 0});
        }
        else
        {
            dashboard.add_widget("samlab-generic-content-widget", {service: service, name: name});
        }
    }


    function load_backends()
    {
        server.load_json(module, "/backends");
    }

/*
    object.changed.subscribe(function(object)
    {
        if(object.otype == "experiments")
        {
            load_experiments();
        }
    });

    object.created.subscribe(function(object)
    {
        if(object.otype == "experiments")
        {
            load_experiments();
        }
    });

    object.deleted.subscribe(function(object)
    {
        if(object.otype == "experiments")
        {
            load_experiments();
        }
    });
*/

    load_backends();

    return module;
});
