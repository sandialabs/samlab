// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-object",
    "samlab-server",
    ], function(ko, mapping, dashboard, object, server)
{
    var component_name = "samlab-video-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    content_type: widget.params["content-type"],
                    label: object.label(widget.params.otype, {singular: true, capitalize: true}) + " Content",
                    metadata: {size: []},
                    oid: widget.params.oid,
                    otype: widget.params.otype,
                    role: widget.params.role,
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, widget.params.otype, widget.params.oid);

                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                }

                component.uri = ko.pureComputed(function()
                {
                    return "/" + component.otype() + "/" + component.oid() + "/content/" + component.role() + "/data";
                });

/*
                component.metadata.size_formatted = ko.pureComputed(function()
                {
                    return component.metadata.size().join(" \u00d7 ");
                });

                server.load_json(component, "/" + component.otype() + "/" + component.oid() + "/content/" + component.role() + "/image/metadata");
*/

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { },
    };

    return module;
});
