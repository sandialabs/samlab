// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-experiment",
    ], function(ko, mapping, dashboard, experiment)
{
    var component_name = "samlab-experiments-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                });

                component.experiments = experiment.experiments.map(function(experiment)
                {
                    return { label: experiment.name, id: experiment.id};
                });

                component.open_experiment = function(item)
                {
                    dashboard.add_widget("samlab-experiment-widget", {id: item.id});
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
