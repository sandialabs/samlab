// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "element-resize-event",
    "jquery",
    "knockout",
    "knockout.mapping",
    ], function(resize_event, jquery, ko, mapping)
{
    var component_name = "samlab-widget-layout-test-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    width: null,
                    height: null,
                });

                var container = jquery(component_info.element.querySelector(".test-container"));

                resize_event(container[0], function()
                {
                    component.width(container.innerWidth());
                    component.height(container.innerHeight());
                });

                return component;
            },
        },

        template: { require: "text!" + component_name + ".html" },
    });

    var module =
    {
        widget: { params: {state: ""}},
    };

    return module;
});
