// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout", "knockout.mapping", "samlab-dashboard", "samlab-dialog"], function(ko, mapping, dashboard, dialog)
{
    var component_name = "samlab-keyboard-test-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    last_key: null,
                    last_time: null,
                });

                component.activate_key = function(event, key)
                {
                    component.last_key(key);
                    component.last_time(new Date().toLocaleTimeString());
                };

                component.modal_test = function()
                {
                    dialog.dialog(
                    {
                        title: "Modal Test",
                        message: "This dialog doesn't block keyboard input from the widget below.",
                    });
                }

                dashboard.bind({widget: widget, keys: "left", callback: component.activate_key});
                dashboard.bind({widget: widget, keys: "right", callback: component.activate_key});

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
