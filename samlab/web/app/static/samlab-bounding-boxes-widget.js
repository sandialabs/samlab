// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["debug", "knockout", "knockout.mapping", "samlab-dashboard"], function(debug, ko, mapping, dashboard)
{
    var component_name = "samlab-bounding-boxes-widget";
    var log = debug(component_name);

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    otype: widget.params.otype(),
                    oid: widget.params.oid(),
                    key: widget.params.key(),
                    title: "Bounding Boxes Editor",
                });

                component.src = ko.pureComputed(function()
                {
                    return "/" + component.otype() + "/" + component.oid() + "/content/" + component.key() + "/data";
                });

                return component;
            },
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { params: {otype: null, oid: null, key: null}},
    };

    return module;
});

