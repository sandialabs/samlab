// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    ], function(ko, mapping)
{
    var component_name = "samlab-image-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    uri: widget.params.uri,
//                    content_type: widget.params["content-type"],
//                    label: object.label(widget.params.otype, {singular: true, capitalize: true}),
                    metadata: {size: [0, 0]},
//                    oid: widget.params.oid,
//                    otype: widget.params.otype,
//                    key: widget.params.key,
                });

                component.metadata.size_formatted = ko.pureComputed(function()
                {
                    return component.metadata.size().join(" \u00d7 ");
                });

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { },
    };

    return module;
});
