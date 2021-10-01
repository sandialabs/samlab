// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-services",
    ], function(debug, ko, mapping, dashboard, services)
{
    var component_name = "samlab-services-widget";
    var log = debug(component_name);

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                });

                component.backends = services.backends.map(function(backend)
                {
                    return { service: backend.service, name: backend.name};
                });

                component.show_service = function(item)
                {
                    dashboard.show_service(item.service(), item.name());
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
