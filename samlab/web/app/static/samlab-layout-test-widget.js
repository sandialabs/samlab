// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout", "knockout.mapping"], function(ko, mapping)
{
    var component_name = "samlab-layout-test-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    x: widget.x,
                    y: widget.y,
                    width: widget.width,
                    height: widget.height,
                });

                component.state = widget.params.state;

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
