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
                    notify.show({icon: "bi-house", message: "Local notification."});
                }

                component.broadcast = function()
                {
                    notify.broadcast({icon: "bi-broadcast", message: "Broadcast notification."});
                }

                component.delayed_broadcast = function()
                {
                    notify.show({icon: "bi-hourglass-top", message: "Start delayed broadcast notification."});
                    notify.broadcast({delay: 5, icon: "bi-hourglass-bottom", message: "Finish delayed broadcast notification."});
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
