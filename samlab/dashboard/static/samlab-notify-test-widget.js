// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout", "knockout.mapping", "samlab-notify"], function(ko, mapping, notify)
{
    var component_name = "samlab-notify-test-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                });

                component.local = function()
                {
                    notify.local({icon: "bi-house", message: "Local notification.", autohide: 5});
                }

                component.broadcast = function()
                {
                    notify.broadcast({icon: "bi-broadcast", message: "Broadcast notification.", autohide: 5});
                }

                component.delayed_broadcast = function()
                {
                    notify.local({icon: "bi-hourglass-top", message: "Start delayed broadcast notification.", autohide: 5});
                    notify.broadcast({icon: "bi-hourglass-bottom", message: "Finish delayed broadcast notification.", delay: 5, autohide: 5});
                }

                return component;
            },
        },

        template: { require: "text!" + component_name + ".html" },
    });

    var module =
    {
        widget: { },
    };

    return module;
});
