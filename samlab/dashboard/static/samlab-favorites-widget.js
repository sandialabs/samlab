// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "lodash",
    "samlab-dashboard",
    "samlab-favorites",
    "samlab-services",
    ], function(ko, mapping, lodash, dashboard, favorites, services)
{
    var component_name = "samlab-favorites-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                });

                component.groups = ko.computed(function()
                {
                    var grouped = lodash.groupBy(favorites.favorites(), function(favorite)
                    {
                        return services.label(favorite.service());
                    });

                    var result = [];
                    for(key in grouped)
                        result.push({"label": key, "items": grouped[key]});

                    result = lodash.sortBy(result, ["label"]);

                    return result;
                });

                component.show_favorite = function(favorite)
                {
                    dashboard.show_service(favorite.service, favorite.name);
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
