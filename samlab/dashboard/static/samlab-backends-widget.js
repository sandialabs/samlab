// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-backends",
    "samlab-dashboard",
    ], function(ko, mapping, backends, dashboard)
{
    var component_name = "samlab-backends-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                });

                component.backends = backends.backends.map(function(backend)
                {
                    return { service: backend.service, name: backend.name};
                });

                component.open_backend = function(item)
                {
                    //dashboard.add_widget("samlab-dataset-widget", {id: item.id});
                };

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
