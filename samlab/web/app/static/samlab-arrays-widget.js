// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-object-manager",
    "samlab-server",
    ], function(ko, mapping, dashboard, object, server)
{
    var component_name = "samlab-arrays-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    content_type: widget.params["content-type"],
                    metadata: [],
                    label: object.label(widget.params.otype, {singular: true, capitalize: true}) + " Content",
                    oid: widget.params.oid,
                    otype: widget.params.otype,
                    key: widget.params.key,
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, widget.params.otype, widget.params.oid);

                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                }

                server.load_json(component, "/" + component.otype() + "/" + component.oid() + "/content/" + component.key() + "/arrays/metadata");

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: {},
    };

    return module;
});
