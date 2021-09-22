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
    var log = debug("samlab-content-manager");

    var module = {};

    var content_widget_map = {
        "application/x-keras-artifact": "samlab-keras-artifact-widget",
        "application/x-numpy-array": "samlab-array-widget",
        "application/x-numpy-arrays": "samlab-arrays-widget",
        "application/x-wavefront-obj": "samlab-3d-viewer-widget",
        "artifact/stl": "samlab-3d-viewer-widget",
        "image/jpeg": "samlab-image-widget",
        "image/png": "samlab-image-widget",
        "text/plain": "samlab-text-widget",
        "video/mp4": "samlab-video-widget",
        "video/quicktime": "samlab-video-widget",
    };

    module.is_image = function(content_type)
    {
        type_subtype = ko.unwrap(content_type).split(";")[0];
        type = type_subtype.split("/")[0];
        return type == "image";
    }

    module.show = function(otype, oid, key, content_type)
    {
        otype = ko.unwrap(otype);
        oid = ko.unwrap(oid);
        key = ko.unwrap(key);
        content_type = ko.unwrap(content_type);

        log("show", otype, oid, key, content_type);

        type_subtype = content_type.split(";")[0];

        if(type_subtype == "application/x-samlab-widget")
        {
            server.get_json("/" + otype + "/" + oid + "/content/" + key + "/data",
            {
                success: function(widget)
                {
                    dashboard.add_widget(widget.component, widget.params);
                }
            });
        }
        else
        {
            var widget = "samlab-generic-content-widget";
            if(type_subtype in content_widget_map)
                widget = content_widget_map[type_subtype];

            dashboard.add_widget(widget, {otype: otype, oid: oid, key: key, "content-type": content_type});
        }
    }

    return module;
});

