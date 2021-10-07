// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    ], function(ko, mapping, dashboard)
{
    var component_name = "samlab-generic-content-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    service: widget.params.service,
                    name: widget.params.name,
                });

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });
});
