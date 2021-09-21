// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-dataset-manager",
    ], function(ko, mapping, dashboard, dataset_manager)
{
    var component_name = "samlab-datasets-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                });

                component.datasets = dataset_manager.datasets.map(function(dataset)
                {
                    return { label: dataset, id: dataset};
                });

                component.open_dataset = function(item)
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
