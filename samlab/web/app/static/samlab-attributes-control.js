// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-object",
    "samlab-server",
    "URI",
    ], function(debug, ko, mapping, object, server, URI)
{
    var component_name = "samlab-attributes-control";

    var log = debug(component_name);

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(params, component_info)
            {
                var component = mapping.fromJS({
                    otype: params.otype,
                    oid: params.oid,
                    markup: "Loading &hellip;",
                    expanded: false,
                });

                var change_subscription = object.notify_changed(component.otype, component.oid, function()
                {
                    component.load_markup();
                });

                component.dispose = function()
                {
                    change_subscription.dispose();
                }

                component.toggle_expanded = function()
                {
                    component.expanded(!component.expanded());
                }

                component.load_markup = function()
                {
                    log("load_markup");
                    if(component.otype() == null || component.oid() == null)
                        return;

                    var uri = new URI("/" + component.otype() + "/" + component.oid());
                    if(component.expanded())
                        uri.path(uri.path() + "/attributes/pre");
                    else
                        uri.path(uri.path() + "/attributes/summary");

                    server.load_text(uri, function(value)
                    {
                        component.markup(value);
                    });
                };

                component.auto_load_markup = ko.computed(function()
                {
                    component.load_markup();
                });

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });
});
