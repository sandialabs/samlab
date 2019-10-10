// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-socket",
    ], function(debug, ko, mapping, socket)
{
    var log = debug("samlab-timeseries");

    var module = mapping.fromJS({
        changed: null,
    });

    module.changed.extend({notify: "always"});

    socket.on("timeseries-changed", function(object)
    {
        log("timeseries changed", object);
        module.changed(object);
    });

    module.notify_changed = function(key, callback)
    {
        var key = ko.unwrap(key)
        return module.changed.subscribe(function(object)
        {
            if(object.key.startsWith(key))
            {
                callback();
            }
        });
    }


    return module;
});

