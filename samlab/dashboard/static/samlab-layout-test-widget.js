// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["debug", "knockout", "knockout.mapping"], function(debug, ko, mapping)
{
    var component_name = "samlab-layout-test-widget";
    var log = debug(component_name);

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
                    contentWidth: 0,
                    contentHeight: 0,
                });

                var observer = new ResizeObserver(function(entries, observer)
                {
                    component.contentWidth(entries[0].contentRect.width);
                    component.contentHeight(entries[0].contentRect.height);
                });
                observer.observe(component_info.element.querySelector(".widget-content"));

                return component;
            },
        },

        template: { require: "text!" + component_name + ".html" },
    });

    var module =
    {
        widget: { params: {}},
    };

    return module;
});
